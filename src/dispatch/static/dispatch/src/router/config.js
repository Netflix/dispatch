import { DefaultLayout, DashboardLayout, BasicLayout } from "@/components/layouts"

export const publicRoute = [
  {
    path: "*",
    component: () => import(/* webpackChunkName: "errors-404" */ "@/views/error/NotFound.vue")
  },
  {
    path: "/auth",
    component: BasicLayout,
    meta: { title: "Auth", icon: "view_compact", group: "auth" },
    children: [
      {
        path: "login",
        name: "Login",
        component: () => import(/* webpackChunkName: "auth-login" */ "@/auth/Login.vue")
      },
      {
        path: "register",
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
    path: "/incidents",
    component: DefaultLayout,
    meta: {
      title: "Incidents",
      icon: "view_compact",
      group: "incidents",
      requiresAuth: true,
      showEditSheet: false
    },
    children: [
      {
        path: "",
        name: "IncidentTable",
        meta: { title: "List" },
        component: () => import(/* webpackChunkName: "incident-table" */ "@/incident/Table.vue"),
        children: [
          {
            path: ":name",
            component: () =>
              import(/* webpackChunkName: "incident-table" */ "@/incident/EditSheet.vue"),
            props: true,
            meta: {
              showEditSheet: true
            }
          }
        ]
      }
    ]
  },
  {
    path: "/tasks",
    component: DefaultLayout,
    meta: { title: "Tasks", icon: "view_compact", group: "tasks", requiresAuth: true },
    children: [
      {
        path: "",
        name: "TaskTable",
        meta: { title: "List" },
        component: () => import(/* webpackChunkName: "task-table" */ "@/task/Table.vue")
      }
    ]
  },
  {
    path: "/feedback",
    component: DefaultLayout,
    meta: { title: "Feedback", icon: "view_compact", group: "feedback", requiresAuth: true },
    children: [
      {
        path: "",
        name: "FeedbackTable",
        meta: { title: "Feedback" },
        component: () => import(/* webpackChunkName: "feedback-table" */ "@/feedback/Table.vue")
      }
    ]
  },
  {
    path: "/dashboard",
    component: DashboardLayout,
    redirect: "/dashboard/incidents",
    meta: { title: "Dashboard", group: "dashboard", icon: "", requiresAuth: true },
    children: [
      {
        path: "incidents",
        name: "IncidentOverview",
        meta: { title: "Incidents", hiddenInMenu: true },
        props: route => ({
          query: route.query
        }),
        component: () =>
          import(/* webpackChunkName: "incident-overview" */ "@/dashboard/IncidentOverview.vue")
      },
      {
        path: "tasks",
        name: "TaskOverview",
        meta: { title: "Tasks", hiddenInMenu: true },
        props: route => ({
          query: route.query
        }),
        component: () =>
          import(/* webpackChunkName: "task-overview" */ "@/dashboard/TaskOverview.vue")
      }
    ]
  },
  {
    path: "/configuration",
    component: DefaultLayout,
    meta: {
      title: "Configuration",
      icon: "view_compact",
      group: "configuration",
      requiresAuth: true
    },
    children: [
      {
        path: "/configuration/incidentCostTypes",
        name: "IncidentCostTypeTable",
        meta: { title: "Incident Cost Types" },
        component: () =>
          import(/* webpackChunkName: "incident-cost-type-table" */ "@/incident_cost_type/Table.vue")
      },
      {
        path: "/configuration/incidentPriorities",
        name: "IncidentPriorityTable",
        meta: { title: "Incident Priorities" },
        component: () =>
          import(/* webpackChunkName: "routing-table" */ "@/incident_priority/Table.vue")
      },
      {
        path: "/configuration/incidentTypes",
        name: "IncidentTypeTable",
        meta: { title: "Incident Types" },
        component: () =>
          import(/* webpackChunkName: "incident-type-table" */ "@/incident_type/Table.vue")
      },
      {
        path: "/configuration/notifications",
        name: "NotificationTable",
        meta: { title: "Notifications" },
        component: () =>
          import(/* webpackChunkName: "notification-table" */ "@/notification/Table.vue")
      },
      {
        path: "/configuration/plugins",
        name: "PluginTable",
        meta: { title: "Plugins" },
        component: () => import(/* webpackChunkName: "plugin-table" */ "@/plugin/Table.vue")
      },
      {
        path: "/configuration/tagTypes",
        name: "TagTypeTable",
        meta: { title: "Tag Types" },
        component: () => import(/* webpackChunkName: "tag-type-table" */ "@/tag_type/Table.vue")
      },
      {
        path: "/configuration/users",
        name: "UserTable",
        meta: { title: "Users" },
        component: () => import(/* webpackChunkName: "users-table" */ "@/auth/Table.vue")
      },
      {
        path: "/configuration/workflows",
        name: "WorkflowTable",
        meta: { title: "Workflows" },
        component: () => import(/* webpackChunkName: "workflows-table" */ "@/workflow/Table.vue")
      }
    ]
  },
  {
    path: "/contact",
    component: DefaultLayout,
    meta: { title: "Contact", icon: "view_compact", group: "contact", requiresAuth: true },
    children: [
      {
        path: "services",
        name: "ServiceTable",
        meta: { title: "Services" },
        component: () => import(/* webpackChunkName: "service-table" */ "@/service/Table.vue")
      },
      {
        path: "individuals",
        name: "IndividualTable",
        meta: { title: "Individuals" },
        component: () => import(/* webpackChunkName: "individual-table" */ "@/individual/Table.vue")
      },
      {
        path: "teams",
        name: "TaamTable",
        meta: { title: "Teams" },
        component: () => import(/* webpackChunkName: "team-table" */ "@/team/Table.vue")
      }
    ]
  },
  {
    path: "/knowledge",
    component: DefaultLayout,
    meta: { title: "Knowledge", icon: "view_compact", group: "knowledge", requiresAuth: true },
    children: [
      {
        path: "tags",
        name: "TagTable",
        meta: { title: "Tags" },
        component: () => import(/* webpackChunkName: "tag-table" */ "@/tag/Table.vue")
      },
      {
        path: "documents",
        name: "DocumentTable",
        meta: { title: "Documents" },
        component: () => import(/* webpackChunkName: "document-table" */ "@/document/Table.vue")
      },
      {
        path: "definitions",
        name: "DefinitionTable",
        meta: { title: "Definitions" },
        component: () => import(/* webpackchunkname: "definition-table" */ "@/definition/Table.vue")
      },
      {
        path: "terms",
        name: "TermTable",
        meta: { title: "Terms" },
        component: () => import(/* webpackChunkName: "term-table" */ "@/term/Table.vue")
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
  }
]
