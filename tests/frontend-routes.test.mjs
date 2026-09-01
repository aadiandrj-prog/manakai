import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const routes = [
  'app/page.tsx',
  'app/product/page.tsx',
  'app/compliance/[id]/page.tsx',
  'app/standards/page.tsx',
  'app/standards/[id]/page.tsx',
  'app/labs/page.tsx',
  'app/ask/page.tsx',
  'app/consumer/page.tsx',
  'app/about/page.tsx',
];

test('all MVP route modules exist', () => {
  for (const route of routes)
    assert.ok(existsSync(route), `${route} should exist`);
});

test('high-risk fixture views disclose demo data', () => {
  for (const route of [
    'app/compliance/[id]/page.tsx',
    'app/labs/page.tsx',
    'app/ask/page.tsx',
  ]) {
    assert.match(readFileSync(route, 'utf8'), /demo|Demo/);
  }
});
