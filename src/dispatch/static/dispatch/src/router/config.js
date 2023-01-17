import { DefaultLayout, DashboardLayout, BasicLayout } from "@/components/layouts"

const registrationEnabled =
  import.meta.env.VITE_DISPATCH_AUTH_REGISTRATION_ENABLED === "false" ? false : true

const withPrefix = (prefix, routes) =>
  routes.map((route) => {
    route.path = prefix + route.path
    return route
  })

const authPages = [
  {
    path: "login",
    name: "BasicLogin",
    component: () => import("@/auth/Login.vue"),
  },
]

if (registrationEnabled) {
  authPages.push({
    path: "register",
    name: "BasicRegister",
    component: () => import("@/auth/Register.vue"),
  })
}

export const publicRoute = [
  {
    path: "*",
    meta: { title: "Dispatch" },
    component: () => import("@/views/error/NotFound.vue"),
  },
  {
    path: "/:organization/auth/",
    component: BasicLayout,
    meta: { title: "Auth", icon: "view_compact", group: "auth" },
    children: authPages,
  },
  {
    path: "/404",
    name: "404",
    meta: { title: "Not Found" },
    component: () => import("@/views/error/NotFound.vue"),
  },
  {
    path: "/500",
    name: "500",
    meta: { title: "Server Error" },
    component: () => import("@/views/error/Error.vue"),
  },
  {
    path: "/implicit/callback",
    name: "PKCEImplicityCallback",
    meta: { requiresAuth: true },
  },
]

// NOTE: The order in which routes are added to the list matters when evaluated. For example, /incidents/report will take precendence over /incidents/:name.
export const protectedRoute = [
  {
    path: "/",
    meta: { requiresAuth: true },
    redirect: {
      name: "IncidentTable",
      params: { organization: "default" },
    },
  },
  ...withPrefix("/:organization/", [
    {
      path: "incidents/status",
      name: "status",
      meta: { title: "Incident Status", requiresAuth: true },
      component: () => import("@/incident/Status.vue"),
    },
    {
      path: "incidents/report",
      name: "report",
      meta: { title: "Report", requiresAuth: true },
      component: () => import("@/incident/ReportForm.vue"),
    },
    {
      path: "cases/status",
      name: "caseStatus",
      meta: { title: "Case Status", requiresAuth: true },
      component: () => import("@/case/Status.vue"),
    },
    {
      path: "cases/report",
      name: "caseReport",
      meta: { title: "Case Report", requiresAuth: true },
      component: () => import("@/case/ReportForm.vue"),
    },
    {
      path: "dashboards",
      component: DashboardLayout,
      name: "dashboards",
      redirect: { name: "IncidentOverview" },
      meta: {
        title: "Dashboards",
        group: "dashboard",
        icon: "mdi-monitor-dashboard",
        menu: true,
        requiresAuth: true,
      },
      children: [
        {
          path: "incidents",
          name: "IncidentOverview",
          meta: { title: "Incidents", group: "type" },
          component: () => import("@/dashboard/incident/IncidentOverview.vue"),
        },
        {
          path: "cases",
          name: "CaseOverview",
          meta: { title: "Cases", group: "type" },
          component: () => import("@/dashboard/case/CaseOverview.vue"),
        },
        {
          path: "tasks",
          name: "TaskOverview",
          meta: { title: "Tasks", group: "type" },
          component: () => import("@/dashboard/task/TaskOverview.vue"),
        },
        {
          path: "data",
          name: "DataOverview",
          meta: { title: "Data", group: "type" },
          component: () => import("@/dashboard/data/DataOverview.vue"),
        },
      ],
    },
    {
      path: "incidents",
      component: DefaultLayout,
      name: "incidents",
      meta: {
        title: "Incidents",
        icon: "mdi-file-multiple",
        group: "incidents",
        requiresAuth: true,
        menu: true,
        showEditSheet: false,
      },
      redirect: { name: "IncidentTable" },
      children: [
        {
          path: "/:organization/incidents",
          name: "IncidentTable",
          meta: { title: "List" },
          component: () => import("@/incident/Table.vue"),
          children: [
            {
              path: "/:organization/incidents/:name",
              name: "IncidentTableEdit",
              component: () => import("@/incident/EditSheet.vue"),
              props: true,
              meta: {
                showEditSheet: true,
              },
            },
          ],
        },
      ],
    },
    {
      path: "cases",
      component: DefaultLayout,
      name: "cases",
      meta: {
        title: "Cases",
        icon: "mdi-briefcase",
        group: "cases",
        requiresAuth: true,
        menu: true,
        showEditSheet: false,
      },
      redirect: { name: "CaseTable" },
      children: [
        {
          path: "/:organization/cases",
          name: "CaseTable",
          meta: { title: "List" },
          component: () => import("@/case/Table.vue"),
          children: [
            {
              path: "/:organization/cases/:name",
              name: "CaseTableEdit",
              component: () => import("@/case/EditSheet.vue"),
              props: true,
              meta: {
                showEditSheet: true,
              },
            },
          ],
        },
      ],
    },
    {
      path: "signals",
      component: DefaultLayout,
      name: "signals",
      meta: {
        title: "Signals",
        icon: "mdi-broadcast",
        group: "signals",
        requiresAuth: true,
        menu: true,
        showEditSheet: false,
      },
      redirect: { name: "SignalInstanceTable" },
      children: [
        {
          path: "/:organization/signals",
          name: "SignalInstanceTable",
          meta: { title: "List" },
          component: () => import("@/signal/TableInstance.vue"),
        },
      ],
    },
    {
      path: "data",
      component: DefaultLayout,
      name: "Data",
      redirect: { name: "SourceTable" },
      meta: {
        title: "Data",
        icon: "mdi-database",
        group: "data",
        menu: true,
        requiresAuth: true,
      },
      children: [
        {
          path: "/:organization/data/sources",
          name: "SourceTable",
          meta: { title: "Sources", group: "data" },
          component: () => import("@/data/source/Table.vue"),
        },
        {
          path: "/:organization/data/sources/:name/:tab",
          name: "SourceDetail",
          meta: { title: "Source Detail" },
          component: () => import("@/data/source/Detail.vue"),
        },
        {
          path: "/:organization/data/queries",
          name: "QueryTable",
          meta: { title: "Queries", group: "data" },
          component: () => import("@/data/query/Table.vue"),
        },
      ],
    },
    {
      path: "tasks",
      component: DefaultLayout,
      name: "tasks",
      meta: {
        title: "Tasks",
        icon: "mdi-calendar-check",
        group: "tasks",
        menu: true,
        requiresAuth: true,
      },
      redirect: { name: "TaskTable" },
      children: [
        {
          path: "/:organization/tasks",
          name: "TaskTable",
          meta: { title: "List" },
          component: () => import("@/task/Table.vue"),
        },
      ],
    },
    {
      path: "feedback",
      component: DefaultLayout,
      name: "feedback",
      redirect: { name: "FeedbackTable" },
      meta: {
        title: "Feedback",
        icon: "mdi-message-alert",
        group: "feedback",
        menu: true,
        requiresAuth: true,
      },
      children: [
        {
          path: "/:organization/feedback",
          name: "FeedbackTable",
          meta: { title: "Feedback" },
          component: () => import("@/feedback/Table.vue"),
        },
      ],
    },
    {
      path: "settings",
      component: DefaultLayout,
      name: "settings",
      meta: {
        title: "Settings",
        icon: "mdi-cog",
        group: "settings",
        menu: true,
        requiresAuth: true,
      },
      redirect: { name: "ProjectTable" },
      children: [
        {
          path: "projects",
          name: "ProjectTable",
          meta: {
            title: "Projects",
            subMenu: "organization",
            group: "organization",
          },
          component: () => import("@/project/Table.vue"),
        },
        {
          path: "members",
          name: "OrganizationMemberTable",
          meta: { title: "Members", subMenu: "organization", group: "organization" },
          component: () => import("@/organization/OrganizationMemberTable.vue"),
        },
        {
          path: "projects",
          meta: {
            title: "Project Settings",
            group: "settings",
          },
          name: "ProjectSettings",
          redirect: { name: "PluginTable" },
        },
        ...withPrefix("projects/", [
          {
            path: "plugins",
            name: "PluginTable",
            meta: { title: "Plugins", subMenu: "project", group: "general" },
            component: () => import("@/plugin/Table.vue"),
          },
          {
            path: "notifications",
            name: "NotificationTable",
            meta: { title: "Notifications", subMenu: "project", group: "general" },
            component: () => import("@/notification/Table.vue"),
          },
          {
            path: "workflows",
            name: "WorkflowTable",
            meta: { title: "Workflows", subMenu: "project", group: "general" },
            component: () => import("@/workflow/Table.vue"),
          },
          {
            path: "incidentTypes",
            name: "IncidentTypeTable",
            meta: { title: "Types", subMenu: "project", group: "incident" },
            component: () => import("@/incident/type/Table.vue"),
          },
          {
            path: "incidentPriorities",
            name: "IncidentPriorityTable",
            meta: { title: "Priorities", subMenu: "project", group: "incident" },
            component: () => import("@/incident/priority/Table.vue"),
          },
          {
            path: "incidentSeverities",
            name: "IncidentSeverityTable",
            meta: { title: "Severities", subMenu: "project", group: "incident" },
            component: () => import("@/incident/severity/Table.vue"),
          },
          {
            path: "incidentCostTypes",
            name: "IncidentCostTypesTable",
            meta: { title: "Cost Types", subMenu: "project", group: "incident" },
            component: () => import("@/incident_cost_type/Table.vue"),
          },
          {
            path: "incidentRoles",
            name: "IncidentRolesTable",
            meta: { title: "Roles", subMenu: "project", group: "incident" },
            component: () => import("@/incident_role/Table.vue"),
          },
          {
            path: "caseTypes",
            name: "CaseTypeTable",
            meta: { title: "Types", subMenu: "project", group: "case" },
            component: () => import("@/case/type/Table.vue"),
          },
          {
            path: "casePriorities",
            name: "casePriorityTable",
            meta: { title: "Priorities", subMenu: "project", group: "case" },
            component: () => import("@/case/priority/Table.vue"),
          },
          {
            path: "caseSeverities",
            name: "caseSeverityTable",
            meta: { title: "Severities", subMenu: "project", group: "case" },
            component: () => import("@/case/severity/Table.vue"),
          },
          {
            path: "signals",
            name: "SignalTable",
            meta: { title: "Signal Definitions", subMenu: "project", group: "case" },
            component: () => import("@/signal/Table.vue"),
          },
          {
            path: "source/types",
            name: "SourceTypeTable",
            meta: { title: "Source Types", subMenu: "project", group: "data" },
            component: () => import("@/data/source/type/Table.vue"),
          },
          {
            path: "source/environments",
            name: "SourceEnvironmentTable",
            meta: { title: "Source Environments", subMenu: "project", group: "data" },
            component: () => import("@/data/source/environment/Table.vue"),
          },
          {
            path: "source/statuses",
            name: "SourceStatusTable",
            meta: { title: "Source Statuses", subMenu: "project", group: "data" },
            component: () => import("@/data/source/status/Table.vue"),
          },
          {
            path: "source/transports",
            name: "SourceTransportTable",
            meta: { title: "Source Transports", subMenu: "project", group: "data" },
            component: () => import("@/data/source/transport/Table.vue"),
          },
          {
            path: "source/dataFormats",
            name: "SourceDataFormatTable",
            meta: { title: "Source Data Formats", subMenu: "project", group: "data" },
            component: () => import("@/data/source/dataFormat/Table.vue"),
          },
          {
            path: "templates",
            name: "TemplateTable",
            meta: { title: "Templates", subMenu: "project", group: "documentation" },
            component: () => import("@/document/template/TemplateTable.vue"),
          },
          {
            path: "references",
            name: "ReferenceTable",
            meta: { title: "References", subMenu: "project", group: "documentation" },
            component: () => import("@/document/reference/ReferenceTable.vue"),
          },
          {
            path: "services",
            name: "ServiceTable",
            meta: { title: "Services", subMenu: "project", group: "contact" },
            component: () => import("@/service/Table.vue"),
          },
          {
            path: "individuals",
            name: "IndividualTable",
            meta: { title: "Individuals", subMenu: "project", group: "contact" },
            component: () => import("@/individual/Table.vue"),
          },
          {
            path: "teams",
            name: "TeamTable",
            meta: { title: "Teams", subMenu: "project", group: "contact" },
            component: () => import("@/team/Table.vue"),
          },
          {
            path: "tagTypes",
            name: "TagTypeTable",
            meta: { title: "Tag Types", subMenu: "project", group: "knowledge" },
            component: () => import("@/tag_type/Table.vue"),
          },
          {
            path: "tags",
            name: "TagTable",
            meta: { title: "Tags", subMenu: "project", group: "knowledge" },
            component: () => import("@/tag/Table.vue"),
          },
          {
            path: "runbooks",
            name: "RunbookTable",
            meta: { title: "Runbooks", subMenu: "project", group: "knowledge" },
            component: () => import("@/document/runbook/RunbookTable.vue"),
          },
          {
            path: "definitions",
            name: "DefinitionTable",
            meta: { title: "Definitions", subMenu: "project", group: "knowledge" },
            component: () => import("@/definition/Table.vue"),
          },
          {
            path: "terms",
            name: "TermTable",
            meta: { title: "Terms", subMenu: "project", group: "knowledge" },
            component: () => import("@/term/Table.vue"),
          },
        ]),
      ],
    },
    {
      path: "search",
      name: "GlobalSearch",
      component: DefaultLayout,
      meta: {
        title: "Search",
        icon: "view_compact",
        group: "search",
        noMenu: true,
        requiresAuth: true,
      },
      redirect: { name: "ResultList" },
      children: [
        {
          path: "results",
          name: "ResultList",
          component: () => import("@/search/ResultList.vue"),
        },
      ],
    },
  ]),
]
