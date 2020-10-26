import { DefaultLayout, DashboardLayout, AuthLayout } from "@/components/layouts"

export const publicRoute = [
  {
    path: "*",
    component: () => import(/* webpackChunkName: "errors-404" */ "@/views/error/NotFound.vue")
  },
  {
    path: "/login",
    component: AuthLayout,
    meta: { title: "Login", icon: "view_compact", group: "auth" },
    children: [
      {
        path: "/login",
        name: "Login",
        component: () => import(/* webpackChunkName: "auth-login" */ "@/auth/Login.vue")
      }
    ]
  },
  {
    path: "/register",
    component: AuthLayout,
    meta: { title: "Register", icon: "view_compact", group: "auth" },
    children: [
      {
        path: "/register",
        name: "Register",
        component: () => import(/* webpackChunkName: "auth-register" */ "@/auth/Register.vue")
      }
    ]
  },
  {
    path: "/404",
    name: "404",
    meta: { title: "Not Found" },
    component: () => import(/* webpackChunkName: "errors-404" */ "@/views/error/NotFound.vue")
  },
  {
    path: "/500",
    name: "500",
    meta: { title: "Server Error" },
    component: () => import(/* webpackChunkName: "errors-500" */ "@/views/error/Error.vue")
  }
]

// NOTE: The order in which routes are added to the list matters when evaluated. For example, /incidents/report will take precendence over /incidents/:name.
export const protectedRoute = [
  {
    path: "/",
    component: DefaultLayout,
    meta: { title: "Dispatch", group: "incidents", icon: "", requiresAuth: true },
    redirect: "/dashboard/incidents"
  },
  {
    path: "/dashboard",
    component: DashboardLayout,
    redirect: "/dashboard/incidents",
    meta: { title: "Dashboard", group: "incidents", icon: "", requiresAuth: true },
    children: [
      {
        path: "incidents",
        name: "IncidentOverview",
        meta: { hiddenInMenu: true },
        props: route => ({
          query: route.query
        }),
        component: () =>
          import(/* webpackChunkName: "incident-overview" */ "@/dashboard/IncidentOverview.vue")
      },
      {
        path: "tasks",
        name: "TaskOverview",
        meta: { hiddenInMenu: true },
        props: route => ({
          query: route.query
        }),
        component: () =>
          import(/* webpackChunkName: "task-overview" */ "@/dashboard/TaskOverview.vue")
      }
    ]
  },
  {
    path: "/incidents/status",
    meta: { title: "Status", icon: "", requiresAuth: true },
    component: () => import(/* webpackChunkName: "incidents-status" */ "@/incident/Status.vue")
  },

  {
    path: "/incidents/report",
    meta: { title: "Report", icon: "", requiresAuth: true },
    component: () => import(/* webpackChunkName: "incidents-report" */ "@/incident/ReportForm.vue")
  },
  {
    path: "/incidents/types",
    component: DefaultLayout,
    meta: {
      title: "Incident Types",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/incidents/types",
        name: "IncidentTypeTable",
        component: () => import(/* webpackChunkName: "routing-table" */ "@/incident_type/Table.vue")
      }
    ]
  },
  {
    path: "/incidents/priorities",
    component: DefaultLayout,
    meta: {
      title: "Incident Priorities",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/incidents/priorities",
        name: "IncidentPriorityTable",
        component: () =>
          import(/* webpackChunkName: "routing-table" */ "@/incident_priority/Table.vue")
      }
    ]
  },
  {
    path: "/incidents",
    component: DefaultLayout,
    meta: { title: "Incidents", icon: "view_compact", group: "incidents", requiresAuth: true },
    children: [
      {
        path: "/incidents",
        name: "IncidentTable",
        component: () => import(/* webpackChunkName: "incident-table" */ "@/incident/Table.vue")
      },
      {
        path: "/incidents/:name",
        name: "IncidentTable",
        component: () => import(/* webpackChunkName: "incident-table" */ "@/incident/Table.vue"),
        props: true
      }
    ]
  },
  {
    path: "/services",
    component: DefaultLayout,
    meta: { title: "Services", icon: "view_compact", group: "contacts", requiresAuth: true },
    children: [
      {
        path: "/services",
        name: "ServiceTable",
        component: () => import(/* webpackChunkName: "service-table" */ "@/service/Table.vue")
      }
    ]
  },
  {
    path: "/individuals",
    component: DefaultLayout,
    meta: { title: "Individuals", icon: "view_compact", group: "contacts", requiresAuth: true },
    children: [
      {
        path: "/individuals",
        name: "IndividualTable",
        component: () => import(/* webpackChunkName: "individual-table" */ "@/individual/Table.vue")
      }
    ]
  },
  {
    path: "/teams",
    component: DefaultLayout,
    meta: { title: "Teams", icon: "view_compact", group: "contacts", requiresAuth: true },
    children: [
      {
        path: "/teams",
        name: "TeamTable",
        component: () => import(/* webpackChunkName: "team-table" */ "@/team/Table.vue")
      }
    ]
  },
  {
    path: "/tags/types",
    component: DefaultLayout,
    meta: {
      title: "Tag Types",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/tags/types",
        name: "TagTypeTable",
        component: () => import(/* webpackChunkName: "routing-table" */ "@/tag_type/Table.vue")
      }
    ]
  },
  {
    path: "/tags",
    component: DefaultLayout,
    meta: { title: "Tags", icon: "view_compact", group: "contacts", requiresAuth: true },
    children: [
      {
        path: "/tags",
        name: "TagTable",
        component: () => import(/* webpackChunkName: "tag-table" */ "@/tag/Table.vue")
      }
    ]
  },
  {
    path: "/search",
    component: DefaultLayout,
    meta: { title: "Search", icon: "view_compact", group: "search", requiresAuth: true },
    children: [
      {
        path: "/search",
        name: "ResultList",
        component: () =>
          import(/* webpackChunkName: "search-result-list" */ "@/search/ResultList.vue")
      }
    ]
  },
  {
    path: "/documents",
    component: DefaultLayout,
    meta: { title: "Documents", icon: "view_compact", group: "knowledge", requiresAuth: true },
    children: [
      {
        path: "/documents",
        name: "DocumentTable",
        component: () => import(/* webpackChunkName: "definition-table" */ "@/document/Table.vue")
      }
    ]
  },
  {
    path: "/workflows",
    component: DefaultLayout,
    meta: { title: "Workflows", icon: "view_compac", group: "knowledge", requiresAuth: true },
    children: [
      {
        path: "/workflows",
        name: "WorkflowTable",
        component: () => import(/* webpackChunkName: "definition-table" */ "@/workflow/Table.vue")
      }
    ]
  },
  {
    path: "/definitions",
    component: DefaultLayout,
    meta: { title: "Definitions", icon: "view_compact", group: "knowledge", requiresAuth: true },
    children: [
      {
        path: "/Definitions",
        name: "DefinitionTable",
        component: () => import(/* webpackChunkName: "definition-table" */ "@/definition/Table.vue")
      }
    ]
  },
  {
    path: "/tasks",
    component: DefaultLayout,
    meta: { title: "Tasks", icon: "view_compact", group: "incident", requiresAuth: true },
    children: [
      {
        path: "/tasks",
        name: "TaskTable",
        component: () => import(/* webpackChunkName: "knowledge-table" */ "@/task/Table.vue")
      }
    ]
  },
  {
    path: "/feedback",
    component: DefaultLayout,
    meta: { title: "Feedback", icon: "view_compact", group: "incident", requiresAuth: true },
    children: [
      {
        path: "/feedback",
        name: "FeedbackTable",
        component: () => import(/* webpackChunkName: "knowledge-table" */ "@/feedback/Table.vue")
      }
    ]
  },
  {
    path: "/terms",
    component: DefaultLayout,
    meta: { title: "Terms", icon: "view_compact", group: "knowledge", requiresAuth: true },
    children: [
      {
        path: "/terms",
        name: "TermTable",
        component: () => import(/* webpackChunkName: "knowledge-table" */ "@/term/Table.vue")
      }
    ]
  },
  {
    path: "/policies",
    component: DefaultLayout,
    meta: { title: "Policies", icon: "view_compact", group: "routing", requiresAuth: true },
    children: [
      {
        path: "/policies",
        name: "PoliciesTable",
        component: () => import(/* webpackChunkName: "policy-table" */ "@/policy/Table.vue")
      }
    ]
  },
  //{
  //  path: "/route",
  //  component: DefaultLayout,
  //  meta: { title: "Route", icon: "view_compact", group: "routing", requiresAuth: true },
  //  children: [
  //    {
  //      path: "/route",
  //      name: "RouteTable",
  //      component: () => import(/* webpackChunkName: "routing-table" */ "@/route/Table.vue")
  //    }
  //  ]
  //},
  {
    path: "/plugins",
    component: DefaultLayout,
    meta: {
      title: "Plugins",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/plugins",
        name: "PluginTable",
        component: () => import(/* webpackChunkName: "routing-table" */ "@/plugin/Table.vue")
      }
    ]
  },
  {
    path: "/users",
    component: DefaultLayout,
    meta: {
      title: "Users",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/users",
        name: "UserTable",
        component: () => import(/* webpackChunkName: "routing-table" */ "@/auth/Table.vue")
      }
    ]
  }
]
