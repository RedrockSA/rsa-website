import { defineCollection, z } from 'astro:content';

const pages = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().default('Redrock Strategic Advisors'),
    hero: z.object({
      heading: z.string(),
      subheading: z.string().optional(),
      backgroundImage: z.string(),
      cta: z.array(z.object({
        text: z.string(),
        href: z.string(),
        style: z.enum(['primary', 'secondary']).default('primary'),
      })).optional(),
      height: z.string().optional(),              // e.g. "40vh", "300px" — defaults to "60vh"
    }).optional(),
    pageWidth: z.enum(['narrow', 'wide']).default('wide'),
    draft: z.boolean().default(false),
    showTitle: z.boolean().default(true),
  }),
});

const transactions = defineCollection({
  type: 'content',
  schema: z.object({
    date: z.string(),                                    // ISO date for sorting (announce date)
    clientName: z.string(),                              // client display name (fallback if no logo)
    clientLogo: z.string().optional(),                   // filename in /logos/ e.g. "albion-minerals.png"
    actionText: z.string(),                              // e.g. "has been acquired by", "acquired"
    counterparties: z.array(z.object({                   // 1–3 counterparties
      name: z.string(),                                  // display name (fallback if no logo)
      logo: z.string().optional(),                       // filename in /logos/ e.g. "balchem.png"
    })).min(1),
    transactionType: z.enum([
      'Sell-Side M&A',
      'Buy-Side M&A',
      'Capital Advisory',
      'Strategic Advisory',
    ]),
    industries: z.array(z.string()),                     // e.g. ["Consumer", "Healthcare"]
    dealFeatures: z.array(z.string()).nullable().transform(v => v ?? []),                   // e.g. ["Family & Founder-Owned", "Private Equity"]
    counterpartyLayout: z.enum(['stacked', 'side-by-side']).default('stacked'),  // logo arrangement
    link: z.string().optional(),                         // optional click-through URL
  }),
});

const news = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    description: z.string(),
  }),
});

export const collections = { pages, transactions, news };
