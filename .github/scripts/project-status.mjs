// Moves the issues a pull request links to across the "Kanban Evolt" board
// (GitHub Projects), so the board follows the work without anyone dragging cards.
//
// In Actions it reads the pull_request event. Locally it can replay a PR:
//   PROJECT_TOKEN=$(gh auth token) node .github/scripts/project-status.mjs --pr 205 --dry-run
//
// Rules (docs/ci-cd.md, "Kanban automation"):
// - A PR links an issue with "Refs #N", "Closes #N", "Fixes #N" or "Resolves #N" in its body.
// - Task issues: PR opened or ready → "In review"; draft → "In progress"; merged → "Done".
// - Story issues (title "US-…"): only the story PR (base develop or main) moves them the same
//   way; a task PR into the story branch just takes the story to "In progress".
// - A card never leaves "Done", and a story never goes back from "In review".
// - A PR closed without merging moves nothing.

import { readFileSync } from 'node:fs'

const token = process.env.PROJECT_TOKEN
const owner = process.env.PROJECT_OWNER ?? 'UB-ES-F3-2026'
const projectNumber = Number(process.env.PROJECT_NUMBER ?? '4')
const repoFullName = process.env.GITHUB_REPOSITORY ?? 'UB-ES-F3-2026/F3-Evolt'
const args = process.argv.slice(2)
const dryRun = args.includes('--dry-run')

const STATUS = { progress: 'In progress', review: 'In review', done: 'Done' }
const RANK = { Backlog: 0, Ready: 1, 'In progress': 2, 'In review': 3, Done: 4 }
const LINK = /\b(?:refs?|close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b[\s:]*((?:#\d+(?:[\s,]*(?:and|i)?[\s,]*)?)+)/gi

async function graphql(query, variables = {}) {
  const response = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  })
  const body = await response.json()
  if (!response.ok || body.errors) {
    throw new Error(`GraphQL: ${JSON.stringify(body.errors ?? body)}`)
  }
  return body.data
}

export function linkedIssueNumbers(text) {
  const numbers = new Set()
  for (const match of (text ?? '').matchAll(LINK)) {
    for (const ref of match[1].matchAll(/#(\d+)/g)) numbers.add(Number(ref[1]))
  }
  return [...numbers]
}

/** The column a PR event asks for, or null when it should move nothing. */
export function targetFor({ action, draft, merged }) {
  if (action === 'closed') return merged ? STATUS.done : null
  if (draft || action === 'converted_to_draft') return STATUS.progress
  return STATUS.review
}

/** Final column for one issue, or null to leave it where it is. */
export function decide({ isStory, isStoryPr, target, current }) {
  const wanted = isStory && !isStoryPr ? STATUS.progress : target
  if (current === STATUS.done) return null
  if (isStory && RANK[wanted] < (RANK[current] ?? -1)) return null
  return wanted === current ? null : wanted
}

async function loadPr(number) {
  const [repoOwner, name] = repoFullName.split('/')
  const data = await graphql(
    `query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $number) { number body isDraft merged state baseRefName }
      }
    }`,
    { owner: repoOwner, name, number },
  )
  const pr = data.repository.pullRequest
  const action = pr.state === 'OPEN' ? 'opened' : 'closed'
  return { number: pr.number, body: pr.body, draft: pr.isDraft, merged: pr.merged, base: pr.baseRefName, action }
}

function prFromEvent() {
  const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'))
  const pr = event.pull_request
  return { number: pr.number, body: pr.body, draft: pr.draft, merged: pr.merged, base: pr.base.ref, action: event.action }
}

async function loadProject() {
  const data = await graphql(
    `query($owner: String!, $number: Int!) {
      organization(login: $owner) {
        projectV2(number: $number) {
          id
          field(name: "Status") { ... on ProjectV2SingleSelectField { id options { id name } } }
        }
      }
    }`,
    { owner, number: projectNumber },
  )
  const project = data.organization.projectV2
  return { id: project.id, fieldId: project.field.id, options: new Map(project.field.options.map((o) => [o.name, o.id])) }
}

async function loadIssue(number, projectId) {
  const [repoOwner, name] = repoFullName.split('/')
  const data = await graphql(
    `query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        issueOrPullRequest(number: $number) {
          __typename
          ... on Issue {
            id title
            projectItems(first: 20) {
              nodes {
                id
                project { id }
                fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
              }
            }
          }
        }
      }
    }`,
    { owner: repoOwner, name, number },
  )
  const node = data.repository.issueOrPullRequest
  if (!node || node.__typename !== 'Issue') return null
  const item = node.projectItems.nodes.find((n) => n.project.id === projectId)
  return { id: node.id, title: node.title, itemId: item?.id ?? null, current: item?.fieldValueByName?.name ?? null }
}

async function moveTo(project, issue, column) {
  let itemId = issue.itemId
  if (!itemId) {
    const added = await graphql(
      `mutation($project: ID!, $content: ID!) {
        addProjectV2ItemById(input: { projectId: $project, contentId: $content }) { item { id } }
      }`,
      { project: project.id, content: issue.id },
    )
    itemId = added.addProjectV2ItemById.item.id
  }
  await graphql(
    `mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $project, itemId: $item, fieldId: $field, value: { singleSelectOptionId: $option }
      }) { projectV2Item { id } }
    }`,
    { project: project.id, item: itemId, field: project.fieldId, option: project.options.get(column) },
  )
}

async function main() {
  if (!token) {
    console.log('PROJECT_TOKEN is not set: the Kanban is not updated (see docs/ci-cd.md).')
    return
  }
  const prArg = args.indexOf('--pr')
  const pr = prArg >= 0 ? await loadPr(Number(args[prArg + 1])) : prFromEvent()
  const target = targetFor(pr)
  const numbers = linkedIssueNumbers(pr.body)
  console.log(`PR #${pr.number} (${pr.action}, base ${pr.base}) → ${target ?? 'no move'}; linked: ${numbers.map((n) => `#${n}`).join(' ') || 'none'}`)
  if (!target || numbers.length === 0) return

  const project = await loadProject()
  const isStoryPr = pr.base === 'develop' || pr.base === 'main'
  for (const number of numbers) {
    const issue = await loadIssue(number, project.id)
    if (!issue) continue
    const isStory = /^US-\d+/.test(issue.title)
    const column = decide({ isStory, isStoryPr, target, current: issue.current })
    console.log(`  #${number} ${issue.title.slice(0, 50)}: ${issue.current ?? 'not on the board'} → ${column ?? 'unchanged'}`)
    if (column && !dryRun) await moveTo(project, issue, column)
  }
}

// The unit tests import the pure functions above without running anything.
if (process.env.PROJECT_STATUS_TEST !== '1') {
  main().catch((error) => {
    // A board problem (missing permission, rate limit) is not a code problem: warn and stay
    // green in Actions, so the "Kanban" check never looks like a broken build (review on #218).
    // Locally (--pr) the error still exits 1, so a replay that fails is visible.
    if (process.env.GITHUB_ACTIONS === 'true') {
      console.log(`::warning title=Kanban not updated::${error.message}`)
      return
    }
    console.error(error.message)
    process.exit(1)
  })
}
