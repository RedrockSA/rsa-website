/**
 * Deal Market Commentary — hand-maintained, updated quarterly.
 *
 * Read by the Insights page (which shows the latest two) and by the
 * /insights/commentary archive. Edit here; nothing is hardcoded in a page.
 *
 * ORDER is by `date`, newest first — array order no longer matters, so new
 * items can be appended anywhere.
 *
 * `date` accepts "YYYY-MM-DD" or "YYYY-MM" when only the month is known.
 * Items with no date sort to the end, keeping their order here. Add a date to
 * one and it slots into place automatically.
 */
export interface CommentaryItem {
  source: string;
  title: string;
  url: string;
  /** ISO "YYYY-MM-DD", or "YYYY-MM" for month precision. Blank = unknown. */
  date?: string;
}

export const dealCommentary: CommentaryItem[] = [
  {
    source: 'FactSet',
    title: 'U.S. Mergers & Acquisitions Monthly Review: July 2026',
    url: 'https://insight.factset.com/u.s.-mergers-acquisitions-monthly-review-july-2026',
    date: '2026-09-02',
  },
  {
    source: 'Ropes & Gray',
    title: "Dealmaker's Digest: A Top 10 Bulletin — August 2026",
    url: 'https://www.ropesgray.com/en/insights/alerts/2026/08/dealmakers-digest-august-2026',
    date: '2026-08',
  },
  {
    source: 'Ropes & Gray',
    title: 'M&A Overview for May 2026',
    url: 'https://www.ropesgray.com/en/insights/alerts/2026/05/us-pe-market-recap-may-2026',
    date: '2026-05',
  },
  {
    source: 'FactSet',
    title: 'Flashwire U.S. Monthly, April 2026',
    url: 'https://go.factset.com/hubfs/mergerstat_em/monthly/US-Flashwire-Monthly.pdf',
    date: '2026-04',
  },
  {
    source: 'WSJ',
    title: 'Global M&A Surged This Year With Massive AI Deals',
    url: 'https://www.wsj.com/finance/stocks/global-m-a-sent-surging-this-year-with-massive-ai-deals-22b7c5eb',
    date: '2026-07-08',
  },
  {
    source: 'ACG–GF Data',
    title: 'Steady Middle-Market Deal Flow Amid More Selective Financing Conditions in Q2',
    url: 'https://www.acg.org/news-trends/news/gf-data-reports-show-steady-middle-market-deal-flow-amid-more-selective',
    date: '2026-08-27',
  },
  {
    source: 'PwC',
    title: 'US Deals 2026 midyear outlook',
    url: 'https://www.pwc.com/us/en/services/consulting/deals/outlook.html',
    date: '2026-06-17',
  },
  {
    source: 'M&A',
    title: 'Middle Market Continues to Lose Ground as Large Deals Dominate Global M&A',
    url: 'https://www.themiddlemarket.com/news-analysis/middle-market-continues-to-lose-ground-as-large-deals-dominate-global-ma',
    date: '2026-05-11',
  },
  {
    source: 'GF Data',
    title: "Private Equity's Five-Year Rollercoaster",
    url: 'https://gfdata.com/private-equitys-five-year-rollercoaster/',
    date: '2026-02-13',
  },
  {
    source: 'BCG',
    title: 'M&A Outlook 2026: Expectations Are High—Again',
    url: 'https://www.bcg.com/publications/2026/m-and-a-outlook-expectations-are-high-again',
    date: '2026-01-15',
  },
  {
    source: 'PYMNTS',
    title: "Wall Street Banks on 2026 as Big Year for 'Megadeals'",
    url: 'https://www.pymnts.com/news/partnerships-acquisitions/2025/wall-street-banks-on-2026-as-big-year-for-megadeals',
    date: '',
  },
  {
    source: 'Middle Market Growth',
    title: "Breaking the Dam: ACG's 2025 M&A Recap and 2026 Outlook",
    url: 'https://middlemarketgrowth.org/webinar-gf-data-2025-recap-2026-outlook/',
    date: '',
  },
  {
    source: 'WSJ / Baker McKenzie',
    title: "Private Equity's Game Plan for the Next Phase of Growth",
    url: 'https://partners.wsj.com/baker-mckenzie/m-and-a-matters/private-equitys-game-plan-for-the-next-phase-of-growth/',
    date: '',
  },
  {
    source: 'MarketWatch',
    title: "The 'great wealth transfer' is coming. Many people will be rich — but they're not ready.",
    url: 'https://www.marketwatch.com/story/the-great-wealth-transfer-is-coming-many-people-will-be-rich-but-theyre-not-ready-e206232f',
    date: '',
  },
  {
    source: 'WSJ Video',
    title: 'BCG CEO: Half of CEOs Say Their Jobs Depend on Getting AI Right',
    url: 'https://www.wsj.com/video/series/davos-ceobrief-2026/bcg-ceo-half-of-ceos-say-their-jobs-depend-on-getting-ai-right/9E5ADB2D-B05B-4E0A-A6CB-E29B60D6146C',
    date: '',
  },
  {
    source: 'Citizens',
    title: 'M&A Market Set to Broaden as Confidence Surges',
    url: 'https://www.businesswire.com/news/home/20260106652514/en/MA-Market-Set-to-Broaden-as-Confidence-Surges',
    date: '',
  },
  {
    source: 'WSJ',
    title: 'The Break Is Over. Companies Are Jacking Up Prices Again.',
    url: 'https://www.wsj.com/business/price-increases-consumers-businesses-b70e4542',
    date: '',
  },
  {
    source: 'WSJ',
    title: "Farmers Are Aging. Their Kids Don't Want to Be in the Family Business.",
    url: 'https://www.wsj.com/business/family-farms-inheritance-44c9aa17',
    date: '',
  },
  {
    source: 'Medium',
    title: "The Great Wealth Transfer Isn't What the WSJ Tells You It Is",
    url: 'https://medium.com/@tdoherty_96508/the-great-wealth-transfer-isnt-what-you-think-30e967cca4c1',
    date: '',
  },
];

/** Newest first. Undated items keep their authored order, after the dated ones. */
export function sortedCommentary(): CommentaryItem[] {
  const dated = dealCommentary.filter((i) => i.date);
  const undated = dealCommentary.filter((i) => !i.date);
  dated.sort((a, b) => (b.date as string).localeCompare(a.date as string));
  return [...dated, ...undated];
}

/** "2026-08" -> "August 2026"; "2026-08-07" -> "August 7, 2026". */
export function formatCommentaryDate(date?: string): string {
  if (!date) return '';
  const [y, m, d] = date.split('-');
  const month = new Date(Number(y), Number(m) - 1, 1)
    .toLocaleDateString('en-US', { month: 'long' });
  return d ? `${month} ${Number(d)}, ${y}` : `${month} ${y}`;
}
