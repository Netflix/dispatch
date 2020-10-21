const Menu = [
  { header: "Incidents" },
  {
    title: "Dashboard",
    group: "dashboard",
    component: "Dashboard",
    icon: "language",
    href: "/dashboard"
  },
  {
    title: "Incidents",
    group: "incidents",
    component: "Incidents",
    icon: "notification_important",
    href: "/incidents"
  },
  {
    title: "Tasks",
    group: "tasks",
    component: "Tasks",
    icon: "playlist_add_check",
    href: "/tasks"
  },
  {
    title: "Feedback",
    group: "feedback",
    component: "Feedback",
    icon: "feedback",
    href: "/feedback"
  },
  /*{ header: "Routing" },
  {
    title: "Route",
    group: "routing",
    component: "route",
    icon: "place",
    href: "/route"
  },
  {
    title: "Policies",
    group: "routing",
    component: "Policies",
    icon: "clear_all",
    href: "/policies"
  },*/
  { header: "Contacts" },
  {
    title: "Individuals",
    group: "contacts",
    name: "Individuals",
    icon: "person",
    href: "/individuals"
  },
  {
    title: "Teams",
    group: "contacts",
    name: "Teams",
    icon: "people",
    href: "/teams"
  },
  {
    title: "Services",
    group: "contacts",
    name: "Services",
    icon: "room_service",
    href: "/services"
  },
  { header: "Knowledge" },
  {
    title: "Tags",
    group: "contacts",
    name: "Tags",
    icon: "label",
    href: "/tags"
  },
  {
    title: "Documents",
    group: "knowledge",
    name: "Documents",
    icon: "assignment",
    href: "/documents"
  },
  {
    title: "Terms",
    group: "knowledge",
    name: "Terms",
    icon: "layers",
    href: "/terms"
  },
  {
    title: "Definitions",
    group: "knowledge",
    name: "Defintitions",
    icon: "book",
    href: "/definitions"
  },
  { header: "Configuration" },
  {
    title: "Incident Priorities",
    group: "Configuration",
    name: "Incident Priorities",
    icon: "report",
    href: "/incidents/priorities"
  },
  {
    title: "Incident Types",
    group: "Configuration",
    name: "Incident Types",
    icon: "settings",
    href: "/incidents/types"
  },
  {
    title: "Plugins",
    group: "Configuration",
    name: "Plugins",
    icon: "power",
    href: "/plugins"
  },
  {
    title: "Tag Types",
    group: "Configuration",
    name: "Tag Types",
    icon: "label",
    href: "/tags/types"
  },
  {
    title: "Users",
    group: "Configuration",
    name: "Users",
    icon: "account_box",
    href: "/users"
  },
  {
    title: "Workflows",
    group: "workflows",
    component: "Workflows",
    icon: "work",
    href: "/workflows"
  }
]
// reorder menu
Menu.forEach(item => {
  if (item.items) {
    item.items.sort((x, y) => {
      let textA = x.title.toUpperCase()
      let textB = y.title.toUpperCase()
      return textA < textB ? -1 : textA > textB ? 1 : 0
    })
  }
})

export default Menu
