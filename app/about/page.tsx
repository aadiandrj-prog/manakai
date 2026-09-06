import {
  Braces,
  Database,
  GitBranch,
  Layers3,
  ShieldCheck,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';

const layers = [
  {
    icon: Layers3,
    title: 'Workflow surfaces',
    copy: 'Product analysis, standards, compliance journeys, labs, evidence Q&A and consumer mode.',
  },
  {
    icon: GitBranch,
    title: 'Intent and orchestration',
    copy: 'Serializable routing state selects a deterministic workflow before any language generation.',
  },
  {
    icon: ShieldCheck,
    title: 'Compliance rules',
    copy: 'Verified structured records—not model prose—decide legal status and effective-date outcomes.',
  },
  {
    icon: Database,
    title: 'Hybrid evidence layer',
    copy: 'Metadata filters, keyword retrieval, vector candidates, fusion and provenance-aware selection.',
  },
  {
    icon: Braces,
    title: 'Provider abstraction',
    copy: 'Optional AI providers explain evidence after the rules run. If a provider fails, the regulatory result remains unchanged.',
  },
];

export default function AboutPage() {
  return (
    <AppShell current="/about">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1100px]">
          <PageHeader
            eyebrow="System design"
            title="Rules and evidence form the regulatory core"
            description="ManakAI is a regulatory navigation and compliance-planning platform. Conversation makes verified results easier to understand; it does not decide the applicable law."
            action={
              <Badge
                variant="outline"
                className="border-primary/25 text-primary"
              >
                Hackathon MVP
              </Badge>
            }
          />
          <div className="grid gap-4 md:grid-cols-2">
            {layers.map(({ icon: Icon, title, copy }, index) => (
              <article
                key={title}
                className={`panel p-5 ${index === layers.length - 1 ? 'md:col-span-2' : ''}`}
              >
                <div className="icon-box violet">
                  <Icon />
                </div>
                <h2 className="mt-5 font-heading text-lg tracking-[-.035em]">
                  {title}
                </h2>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {copy}
                </p>
              </article>
            ))}
          </div>
          <div className="panel mt-5 p-5">
            <span className="eyebrow">Decision flow</span>
            <div className="mt-5 flex flex-wrap items-center gap-2 text-xs">
              {[
                'Natural-language request',
                'Intent route',
                'Structured retrieval',
                'Rule evaluation',
                'Evidence selection',
                'Action journey',
              ].map((item, index, list) => (
                <div key={item} className="contents">
                  <span className="rounded border border-border bg-[#0c0d0e] px-3 py-2">
                    {item}
                  </span>
                  {index < list.length - 1 && (
                    <span className="text-primary">→</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </AppShell>
  );
}
