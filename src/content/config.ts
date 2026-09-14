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
      contentOffset: z.string().optional(),       // e.g. "5rem" — pushes hero text lower on the image
    }).optional(),
    pageWidth: z.enum(['narrow', 'wide']).default('wide'),
    draft: z.boolean().default(false),
    showTitle: z.boolean().default(true),
    teamGrid: z.boolean().default(false),        // render the team card grid below the page content
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

const team = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),                                    // display name, e.g. "Geoffrey Loos"
    title: z.string(),                                   // e.g. "Managing Director"
    photo: z.string(),                                   // path in /public, e.g. "/team/GeoffLoos.jpg"
    email: z.string(),
    phone: z.string().optional(),
    linkedin: z.string().optional(),                     // full profile URL
    joined: z.string(),                                  // ISO date joined the firm — default sort (longest tenure first)
    order: z.number().optional(),                        // optional manual override; lower numbers come first
    education: z.array(z.string()).default([]),          // one bullet per line
    draft: z.boolean().default(false),
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


const books = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),                     // full title with subtitle, when different
    author: z.string(),
    authorLastName: z.string().optional(),

    isbn13: z.string().optional(),                       // hyphenated, e.g. "978-0-307719218"
    isbn10: z.string().optional(),
    asin: z.string().optional(),
    amazonUrl: z.string().optional(),                    // the affiliate link, straight from the CSV

    publisher: z.string().optional(),
    pages: z.number().optional(),
    yearPublished: z.number().optional(),
    originalPublicationYear: z.number().optional(),

    type: z.enum(['fiction', 'non-fiction']).default('non-fiction'),
    primaryCategory: z.string().optional(),              // one per book - the shelf, and the Primary Category filter
    topics: z.array(z.string()).default([]),             // granular tags, multi-value
    secondaryCategories: z.array(z.string()).default([]), // broad buckets, multi-value
    era: z.string().optional(),
    eraPublished: z.string().optional(),
    geography: z.string().optional(),

    coverImage: z.string().optional(),                   // derived by generate-books.mjs
    coverWidth: z.number().optional(),                   // dimensions of the SHIPPED webp, not the source
    coverHeight: z.number().optional(),

    oneLiner: z.string().default(''),
    featured: z.boolean().default(false),
    myRating: z.number().optional(),                     // private - not rendered publicly
    dateRead: z.coerce.date().optional(),
    dateAdded: z.coerce.date(),
  }),
});

export const collections = { pages, transactions, news, team, books };
