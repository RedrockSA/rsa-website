export interface NavSubItem {
  label: string;
  href: string;
}

export interface NavItem {
  label: string;
  href: string;
  group: 'left' | 'right';
  children?: NavSubItem[];
  dropdownColumns?: 1 | 2;
}

export const navItems: NavItem[] = [
  {
    label: 'Services',
    href: '/services',
    group: 'left',
    dropdownColumns: 1,
    children: [
      { label: 'Mergers & Acquisitions', href: '/services/mergers-and-acquisitions' },
      { label: 'Capital Advisory', href: '/services/capital-advisory' },
      { label: 'Strategic & Board Advisory', href: '/services/strategic-and-board-advisory' },
    ],
  },
  {
    label: 'Transactions',
    href: '/transactions',
    group: 'left',
    
  },
  {
    label: 'Insights',
    href: '/insights',
    group: 'left',
  },
  {
    label: 'Career Path',
    href: '/career-path',
    group: 'right',
  },
  {
    label: 'About Us',
    href: '/about/our-focus',
    group: 'right',
    dropdownColumns: 2,
    children: [
      { label: 'Our Focus', href: '/about/our-focus' },
      { label: 'Team', href: '/about/team' },
      { label: 'Transactions', href: '/transactions' },
      { label: 'Newsroom', href: '/about/newsroom' },
    ],
  },
  {
    label: 'Contact',
    href: '/contact',
    group: 'right',
  },
];
