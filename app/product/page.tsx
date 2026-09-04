'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import {
  ArrowRight,
  Check,
  CircleAlert,
  LoaderCircle,
  Search,
  Sparkles,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

const scenarios = [
  'I manufacture a 1500 W electric kettle for household use in India.',
  'I manufacture motorcycle helmets for two-wheeler riders in India.',
  'We produce OPC 53 ordinary Portland cement in India.',
  'I manufacture a 5 litre domestic pressure cooker in India.',
  'I sell 22K916 gold jewellery with HUID.',
];

export default function ProductPage() {
  const [description, setDescription] = useState(scenarios[0]);
  const [role, setRole] = useState('Manufacturer');
  const [enterpriseCategory, setEnterpriseCategory] = useState('GENERAL');
  const analysis = useMutation({ mutationFn: api.analyse });
  const profile = analysis.data;
  const matched = profile?.applicable_standards[0];
  function analyse() {
    analysis.mutate({ description: description.trim(), role: role.toLowerCase(), language: 'en', enterprise_category: enterpriseCategory });
  }
  return (
    <AppShell current="/product">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow="Discover"
            title="Product compliance analyser"
            description="Describe the product in plain language. ManakAI extracts a structured profile, retrieves candidate standards and hands legal-status decisions to explicit rules."
          />
          <div className="grid gap-5 xl:grid-cols-[.82fr_1.18fr]">
            <div className="panel p-5">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Sparkles className="size-4 text-primary" /> Product description
              </div>
              <label
                htmlFor="description"
                className="mt-5 block text-xs text-muted-foreground"
              >
                What do you make, import, sell or use?
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-2 min-h-32 w-full resize-none rounded-md border border-input bg-[#0b0c0d] p-3 text-sm leading-6 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
              <label
                htmlFor="role"
                className="mt-4 block text-xs text-muted-foreground"
              >
                Your role
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="mt-2 h-10 w-full rounded-md border border-input bg-[#0b0c0d] px-3 text-sm"
              >
                <option>Manufacturer</option>
                <option>Importer</option>
                <option>Seller</option>
                <option>Consumer</option>
              </select>
              <label htmlFor="enterprise-category" className="mt-4 block text-xs text-muted-foreground">Enterprise category for QCO dates</label>
              <select id="enterprise-category" value={enterpriseCategory} onChange={(event) => setEnterpriseCategory(event.target.value)} className="mt-2 h-10 w-full rounded-md border border-input bg-[#0b0c0d] px-3 text-sm">
                <option value="GENERAL">General (not micro/small)</option>
                <option value="SMALL">Small enterprise</option>
                <option value="MICRO">Micro enterprise</option>
              </select>
              <Button
                onClick={analyse}
                disabled={!description.trim() || analysis.isPending}
                className="mt-5 h-11 w-full rounded-md"
              >
                {analysis.isPending ? (
                  <>
                    <LoaderCircle className="animate-spin" /> Analysing database records
                  </>
                ) : (
                  <>
                    <Search /> Analyse product
                  </>
                )}
              </Button>
              <div className="mt-5">
                <div className="eyebrow">Example scenarios</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {scenarios.map((item) => (
                    <button
                      key={item}
                      onClick={() => setDescription(item)}
                      className="rounded border border-border px-2 py-1 text-[11px] text-muted-foreground hover:bg-muted"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div>
              {analysis.isError ? <ErrorState message={errorMessage(analysis.error)} /> : !profile || analysis.isPending ? <LoadingState label={analysis.isPending ? 'Building structured product profile…' : 'Choose an example or describe a product to check published coverage.'} /> : (
                <div className="panel overflow-hidden">
                  <div className="panel-header">
                    <div>
                      <span className="eyebrow">Interpreted product</span>
                      <h2 className="panel-title">{profile.product.interpreted_product}</h2>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Role: {profile.product.role}
                      </p>
                    </div>
                    <Badge className="bg-emerald-400/10 text-emerald-300">
                      {profile.coverage.coverage_status} · {Math.round(profile.confidence * 100)}%
                    </Badge>
                  </div>
                  <div className="grid gap-px bg-border sm:grid-cols-3">
                    <div className="metric">
                      <span>Category</span>
                      <strong className="text-base">{profile.product.category}</strong>
                      <small>Database-backed classifier</small>
                    </div>
                    <div className="metric">
                      <span>Candidate</span>
                      <strong className="text-base">{matched?.number ?? 'No verified mapping'}</strong>
                      <small>{matched?.version ?? profile.coverage.coverage_status}</small>
                    </div>
                    <div className="metric">
                      <span>Status</span>
                      <strong className="text-base text-amber-300">
                        {profile.mandatory_status}
                      </strong>
                      <small>{profile.qco ? `${profile.qco.notification_number} · ${profile.qco.status}` : 'No live QCO source'}</small>
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex gap-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-3">
                      <CircleAlert className="mt-0.5 size-4 shrink-0 text-amber-300" />
                      <p className="text-xs leading-5 text-amber-100/75">
                        {profile.coverage.coverage_reason} {profile.data_mode === 'AUTHORITATIVE' ? `Evidence evaluated as of ${profile.as_of_date}.` : 'Demo data remains separate from authoritative records.'}
                      </p>
                    </div>
                    <div className="mt-5">
                      <div className="eyebrow">Why this candidate</div>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        Product terms align with database-backed category and scope metadata. Regulatory status is evaluated by explicit backend rules.
                      </p>
                    </div>
                    <div className="mt-5 flex flex-wrap gap-2">
                      {matched && <Button
                        nativeButton={false}
                        render={
                          <Link
                            aria-label="Open compliance profile"
                            href={`/compliance/${profile.id}`}
                          />
                        }
                        className="rounded-md"
                      >
                        Open compliance profile <ArrowRight />
                      </Button>}
                      <Button
                        nativeButton={false}
                        render={
                          <Link
                            aria-label="View matched standard"
                            href={`/standards/${matched?.id}`}
                          />
                        }
                        variant="outline"
                        className="rounded-md"
                      >
                        View standard
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {(profile?.product.attributes ?? []).map((attribute) => (
              <div
                key={attribute}
                className="flex items-center gap-2 rounded-md border border-border bg-card p-3 text-xs"
              >
                <Check className="size-3 text-cyan-300" /> {attribute}
              </div>
            ))}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
