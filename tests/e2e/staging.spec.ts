import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';
import type { ComplianceProfile } from '../../lib/api-client';

const citation: ComplianceProfile['evidence'][number] = {
  id: 'citation-qco', document_title: 'Household Electrical Appliances QCO, 2026', document_type: 'QCO',
  standard_number: 'IS 302 (Part 2/Sec 15)', source_url: 'https://www.bis.gov.in/example',
  effective_date: '2026-09-19', retrieved_at: '2026-09-01T00:00:00Z', source_kind: 'AUTHORITATIVE',
  source_authority: 'Bureau of Indian Standards', document_identifier: 'S.O. 1739(E)', status: 'UPCOMING',
  verification_status: 'AUTHORITATIVE', validation_status: 'VALID',
};

const profile: ComplianceProfile = {
  id: 'profile-e2e',
  product: { interpreted_product: '230 V household electric kettle', role: 'manufacturer', category: 'appliances_for_heating_liquids', attributes: [], missing_attributes: [], structured_attributes: { product_type: 'electric_kettle', rated_voltage_v: 230, intended_use: 'household' } },
  applicable_standards: [{ id: 'kettle-standard', number: 'IS 302 (Part 2/Sec 15)', title: 'Safety of household appliances — heating liquids', version: '2009', status: 'ACTIVE', category: 'appliances_for_heating_liquids', scope: 'Electric kettles', source_kind: 'AUTHORITATIVE' }],
  mandatory_status: 'UPCOMING',
  qco: { id: 'qco', title: 'Household Electrical Appliances QCO, 2026', notification_number: 'S.O. 1739(E)', effective_from: '2026-09-19', status: 'UPCOMING', enterprise_category: 'GENERAL', source_url: citation.source_url, source_kind: 'AUTHORITATIVE' },
  certification_scheme: 'Scheme I (ISI Mark Scheme)', tests: [], required_documents: [],
  laboratories: [{ id: 'lab', name: 'BIS Central Laboratory', city: 'Sahibabad', state: 'Uttar Pradesh', standards: ['IS 302 (Part 2/Sec 15)'], capabilities: ['Complete scope'], test_clauses: [], source_kind: 'AUTHORITATIVE', recognition_status: 'RECOGNISED' }],
  next_steps: [
    { title: 'Product classified', status: 'complete', explanation: 'The product category is supported.', next_action: null },
    { title: 'Confirm testing scope', status: 'attention', explanation: 'Review the applicable tests with a recognised laboratory.', next_action: 'Contact a laboratory and confirm its current scope.' },
  ], evidence: [citation], confidence: 0.94, warnings: [], as_of_date: '2026-09-02', data_mode: 'AUTHORITATIVE', explanation: [],
  coverage: { id: 'coverage-kettle', category_slug: 'appliances-for-heating-liquids', category_name: 'Appliances for Heating Liquids', primary_standard: 'IS 302 (Part 2/Sec 15):2009', coverage_status: 'VERIFIED', coverage_reason: 'Official BIS evidence captured.', authoritative_sources_count: 5, known_limitations: [], standard_metadata_available: true, compliance_verified: true },
  regulatory_regime: { id: 'regime-scheme-i', slug: 'scheme-i-product-certification', name: 'Scheme I Product Certification', regime_type: 'PRODUCT_CERTIFICATION', description: 'BIS Standard Mark licensing.' },
  hallmarking_centres: [], consumer_actions: [],
};

function response(message: string, clarification = false) {
  return {
    conversation_id: 'conversation-e2e', language: 'en', intent: 'PRODUCT_COMPLIANCE',
    answer: clarification ? 'What is the rated voltage of the kettle?' : 'IS 302 (Part 2/Sec 15) applies. [E1]',
    clarification_required: clarification, unresolved_attributes: clarification ? ['rated_voltage_v'] : [],
    compliance_profile: profile, evidence: [{ evidence_id: 'E1', citation }], warnings: [], provider: 'deterministic', used_fallback: true,
    messages: [
      { id: 'u1', role: 'user', content: message, language: 'en', created_at: '2026-09-02T00:00:00Z' },
      { id: 'a1', role: 'assistant', content: clarification ? 'What is the rated voltage of the kettle?' : 'IS 302 (Part 2/Sec 15) applies. [E1]', language: 'en', created_at: '2026-09-02T00:00:01Z' },
    ],
  };
}

async function mockApi(page: Page) {
  await page.route('http://localhost:8000/api/v1/chat', async route => {
    const body = route.request().postDataJSON();
    await route.fulfill({ json: response(body.message, !/\b\d{3}\s*v/i.test(body.message)) });
  });
  await page.route('http://localhost:8000/api/v1/conversations/*/messages', async route => {
    const body = route.request().postDataJSON();
    await route.fulfill({ json: response(body.message, false) });
  });
}

async function mockComplianceApi(page: Page, result: ComplianceProfile = profile) {
  await page.route('http://localhost:8000/api/v1/products/analyse', route => route.fulfill({ json: result }));
  await page.route(`http://localhost:8000/api/v1/compliance/${result.id}`, route => route.fulfill({ json: result }));
  await page.route(`http://localhost:8000/api/v1/compliance/${result.id}/journey`, route => route.fulfill({ json: result.next_steps }));
}

test('dashboard and responsive navigation render', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Check what applies to your product' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Check my product' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Ask ManakAI' }).first()).toBeVisible();
  await expect(page.getByText(/Prototype \/ Staging/)).toBeVisible();
});

test('compliance navigation opens a useful empty state instead of a demo 404', async ({ page }) => {
  await page.goto('/compliance');
  await expect(page.getByRole('heading', { name: 'Compliance journey', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'No compliance journey yet' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Check my product' })).toBeVisible();
});

test('dashboard product text is preserved in the analyser', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('What product do you make, import, or sell?').fill('OPC 53 cement in India');
  await page.getByRole('link', { name: 'Check my product' }).click();
  await expect(page.getByLabel('What do you make, import, sell, or use?')).toHaveValue('OPC 53 cement in India');
});

test('product result prioritises status, date, action and progressive evidence', async ({ page }) => {
  await mockComplianceApi(page);
  await page.goto('/product?q=230V%20household%20electric%20kettle');
  await page.getByRole('button', { name: 'Check requirements' }).click();
  await expect(page.getByRole('heading', { name: '230 V household electric kettle' })).toBeVisible();
  await expect(page.getByText('Upcoming requirement')).toBeVisible();
  await page.getByRole('link', { name: /Open action plan/ }).click();
  await expect(page.getByRole('heading', { name: 'What applies and what should you do?' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '2-step compliance journey' })).toBeVisible();
  await page.getByText('View BIS sources', { exact: true }).click();
  await expect(page.getByRole('link', { name: 'Open official source' })).toBeVisible();
});

test('unsupported and partial products explain their evidence boundary', async ({ page }) => {
  const unsupported: ComplianceProfile = { ...profile, id: 'profile-unsupported', applicable_standards: [], qco: null, mandatory_status: 'UNVERIFIED', laboratories: [], evidence: [], next_steps: [], coverage: { ...profile.coverage, id: 'coverage-unsupported', coverage_status: 'UNSUPPORTED', coverage_reason: 'This product is outside the published coverage registry.', known_limitations: [], compliance_verified: false } };
  await mockComplianceApi(page, unsupported);
  await page.goto('/product?q=smart%20toaster');
  await page.getByRole('button', { name: 'Check requirements' }).click();
  await expect(page.getByRole('heading', { name: /can’t verify an end-to-end BIS result/i })).toBeVisible();

  const partial: ComplianceProfile = { ...profile, id: 'profile-partial', coverage: { ...profile.coverage, id: 'coverage-partial', coverage_status: 'PARTIAL', known_limitations: ['Laboratory validity must be confirmed.'], compliance_verified: false }, warnings: ['Laboratory validity must be confirmed.', 'Current certification route needs confirmation.'] };
  await page.unroute('http://localhost:8000/api/v1/products/analyse');
  await mockComplianceApi(page, partial);
  await page.getByLabel('What do you make, import, sell, or use?').fill('domestic pressure cooker');
  await page.getByRole('button', { name: 'Check requirements' }).click();
  await expect(page.getByText('Partial coverage', { exact: true })).toBeVisible();
  await expect(page.getByText('What we could verify')).toBeVisible();
  await expect(page.getByText('Still needs confirmation')).toBeVisible();
  await expect(page.getByText('• Laboratory validity must be confirmed.', { exact: true })).toHaveCount(1);
});

test('authoritative kettle conversation, clarification, evidence and labs', async ({ page }) => {
  await mockApi(page);
  await page.goto('/ask');
  await page.getByLabel(/describe the product/i).fill('I manufacture a household electric kettle.');
  await page.getByRole('button', { name: /^Send/ }).click();
  await expect(page.getByText(/More information needed: rated_voltage_v/)).toBeVisible();
  await page.getByLabel(/continue this compliance analysis/i).fill('230V');
  await page.getByRole('button', { name: /^Send/ }).click();
  await expect(page.getByText('IS 302 (Part 2/Sec 15):2009')).toBeVisible();
  await expect(page.getByText('BIS Central Laboratory')).toBeVisible();
  await expect(page.getByRole('link', { name: /View official source/ })).toHaveAttribute('rel', 'noreferrer');
  await expect(page.getByText('Rules-based fallback', { exact: true })).toBeVisible();
});

test('429 is shown as a controlled staging error', async ({ page }) => {
  await page.route('http://localhost:8000/api/v1/chat', route => route.fulfill({ status: 429, json: { detail: 'Rate limit exceeded. Please try again shortly.' } }));
  await page.goto('/ask');
  await page.getByRole('button', { name: /^Send/ }).click();
  await expect(page.getByText(/Too many requests/)).toBeVisible();
});

test('@a11y core pages have no serious axe violations', async ({ page }) => {
  await mockApi(page);
  for (const path of ['/', '/ask', '/about']) {
    await page.goto(path);
    const results = await new AxeBuilder({ page }).disableRules(['color-contrast']).analyze();
    expect(results.violations.filter(item => ['critical', 'serious'].includes(item.impact ?? ''))).toEqual([]);
  }
});
