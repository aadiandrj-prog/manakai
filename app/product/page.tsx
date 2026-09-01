'use client';

import { useMemo, useState } from 'react';
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
import { emergencyProfile, standards } from '@/lib/demo-data';

const scenarios = [
  'portable rechargeable LED emergency lamp',
  'electric kettle for household use',
  'motorcycle helmet',
];

export default function ProductPage() {
  const [description, setDescription] = useState(scenarios[0]);
  const [role, setRole] = useState('Manufacturer');
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(true);
  const matched = useMemo(
    () =>
      description.toLowerCase().includes('kettle')
        ? standards[1]
        : description.toLowerCase().includes('helmet')
          ? standards[2]
          : standards[0],
    [description],
  );
  function analyse() {
    setLoading(true);
    setComplete(false);
    window.setTimeout(() => {
      setLoading(false);
      setComplete(true);
    }, 650);
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
              <Button
                onClick={analyse}
                disabled={!description.trim() || loading}
                className="mt-5 h-11 w-full rounded-md"
              >
                {loading ? (
                  <>
                    <LoaderCircle className="animate-spin" /> Analysing fixture
                    data
                  </>
                ) : (
                  <>
                    <Search /> Analyse product
                  </>
                )}
              </Button>
              <div className="mt-5">
                <div className="eyebrow">Reliable demo scenarios</div>
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
              {complete ? (
                <div className="panel overflow-hidden">
                  <div className="panel-header">
                    <div>
                      <span className="eyebrow">Interpreted product</span>
                      <h2 className="panel-title">{description}</h2>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Role: {role}
                      </p>
                    </div>
                    <Badge className="bg-emerald-400/10 text-emerald-300">
                      High confidence
                    </Badge>
                  </div>
                  <div className="grid gap-px bg-border sm:grid-cols-3">
                    <div className="metric">
                      <span>Category</span>
                      <strong className="text-base">{matched.category}</strong>
                      <small>Demo classifier</small>
                    </div>
                    <div className="metric">
                      <span>Candidate</span>
                      <strong className="text-base">{matched.number}</strong>
                      <small>{matched.version}</small>
                    </div>
                    <div className="metric">
                      <span>Status</span>
                      <strong className="text-base text-amber-300">
                        Verify
                      </strong>
                      <small>No live QCO source</small>
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex gap-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-3">
                      <CircleAlert className="mt-0.5 size-4 shrink-0 text-amber-300" />
                      <p className="text-xs leading-5 text-amber-100/75">
                        Candidate matching is deterministic in demo mode.
                        Current mandatory status, amendments and official scope
                        must be checked before a regulatory decision.
                      </p>
                    </div>
                    <div className="mt-5">
                      <div className="eyebrow">Why this candidate</div>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        Product terms align with the fixture’s category and
                        scope metadata. No regulatory fact was inferred from the
                        language model.
                      </p>
                    </div>
                    <div className="mt-5 flex flex-wrap gap-2">
                      <Button
                        nativeButton={false}
                        render={
                          <Link
                            aria-label="Open compliance profile"
                            href="/compliance/demo-emergency-lamp"
                          />
                        }
                        className="rounded-md"
                      >
                        Open compliance profile <ArrowRight />
                      </Button>
                      <Button
                        nativeButton={false}
                        render={
                          <Link
                            aria-label="View matched standard"
                            href={`/standards/${matched.id}`}
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
              ) : (
                <div className="panel grid min-h-96 place-items-center">
                  <div className="text-center">
                    <LoaderCircle className="mx-auto size-6 animate-spin text-primary" />
                    <p className="mt-3 text-sm">
                      Building structured product profile…
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {emergencyProfile.attributes.map((attribute) => (
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
