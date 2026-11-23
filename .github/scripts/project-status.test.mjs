// Tests of the Kanban rules (docs/ci-cd.md, "Kanban automation"). Run: node --test .github/scripts/project-status.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'

process.env.PROJECT_STATUS_TEST = '1'
const { linkedIssueNumbers, targetFor, decide } = await import('./project-status.mjs')

test('reads every issue linked with Refs, Closes, Fixes or Resolves', () => {
  assert.deepEqual(linkedIssueNumbers('Refs #148, #184.'), [148, 184])
  assert.deepEqual(linkedIssueNumbers('Closes #181, closes #157, closes #158'), [181, 157, 158])
  assert.deepEqual(linkedIssueNumbers('Fixes #12 i #13\nResolves: #14'), [12, 13, 14])
})

test('ignores numbers that are not linked with a keyword', () => {
  assert.deepEqual(linkedIssueNumbers('Revisat a la #179 i la #194.'), [])
  assert.deepEqual(linkedIssueNumbers(null), [])
})

test('the PR event picks the column', () => {
  assert.equal(targetFor({ action: 'opened', draft: false }), 'In review')
  assert.equal(targetFor({ action: 'ready_for_review', draft: false }), 'In review')
  assert.equal(targetFor({ action: 'opened', draft: true }), 'In progress')
  assert.equal(targetFor({ action: 'converted_to_draft', draft: true }), 'In progress')
  assert.equal(targetFor({ action: 'closed', merged: true }), 'Done')
  assert.equal(targetFor({ action: 'closed', merged: false }), null)
})

test('a task follows its PR, but never leaves Done', () => {
  assert.equal(decide({ isStory: false, isStoryPr: false, target: 'In review', current: 'Backlog' }), 'In review')
  assert.equal(decide({ isStory: false, isStoryPr: false, target: 'Done', current: 'In review' }), 'Done')
  assert.equal(decide({ isStory: false, isStoryPr: false, target: 'In progress', current: 'In review' }), 'In progress')
  assert.equal(decide({ isStory: false, isStoryPr: false, target: 'In review', current: 'Done' }), null)
})

test('a task PR only takes its story to In progress', () => {
  assert.equal(decide({ isStory: true, isStoryPr: false, target: 'Done', current: 'Backlog' }), 'In progress')
  assert.equal(decide({ isStory: true, isStoryPr: false, target: 'In review', current: 'In review' }), null)
  assert.equal(decide({ isStory: true, isStoryPr: false, target: 'Done', current: 'In progress' }), null)
})

test('the story PR moves the story to In review and, merged, to Done', () => {
  assert.equal(decide({ isStory: true, isStoryPr: true, target: 'In review', current: 'In progress' }), 'In review')
  assert.equal(decide({ isStory: true, isStoryPr: true, target: 'Done', current: 'In review' }), 'Done')
})
