import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const routes = [
  'app/page.tsx',
  'app/product/page.tsx',
  'app/compliance/page.tsx',
  'app/compliance/[id]/page.tsx',
  'app/coverage/page.tsx',
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

test('Phase 3A navigation never routes to a stale demo profile', () => {
  const shell = readFileSync('components/manakai/app-shell.tsx', 'utf8');
  const home = readFileSync('app/page.tsx', 'utf8');
  assert.doesNotMatch(shell, /demo-emergency-lamp/);
  assert.doesNotMatch(home, /demo-emergency-lamp/);
  assert.match(shell, /href: '\/compliance'/);
});

test('Phase 3A exposes progressive evidence and useful unsupported states', () => {
  const compliance = readFileSync('app/compliance/[id]/page.tsx', 'utf8');
  const product = readFileSync('app/product/page.tsx', 'utf8');
  assert.match(compliance, /Why does this apply\?/);
  assert.match(compliance, /View BIS sources/);
  assert.match(product, /We can’t verify an end-to-end BIS result/);
  assert.match(product, /Partial coverage/);
});

test('regulatory screens use the typed API and no frontend fixture module remains', () => {
  assert.equal(existsSync('lib/demo-data.ts'), false);
  for (const route of routes) {
    const source = readFileSync(route, 'utf8');
    assert.doesNotMatch(source, /@\/lib\/demo-data/);
  }
  assert.ok(existsSync('lib/api-schema.d.ts'));
  assert.match(readFileSync('lib/api-client.ts', 'utf8'), /components\['schemas'\]/);
});

test('frontend does not scrape or hardcode BIS source endpoints', () => {
  for (const route of routes) {
    const source = readFileSync(route, 'utf8');
    assert.doesNotMatch(source, /bis\.gov\.in|lims\.bis\.gov\.in/);
  }
});
