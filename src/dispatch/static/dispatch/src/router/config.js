import { DefaultLayout, DashboardLayout, BasicLayout } from "@/components/layouts"

const withPrefix = (prefix, routes) =>
  routes.map((route) => {
    route.path = prefix + route.path
    return route
  })

export const publicRoute = [
  {
    path: "*",
    meta: { title: "Dispatch" },
    component: () => import(/* webpackChunkName: "errors-404" */ "@/views/error/NotFound.vue"),
  },
  {
    path: "/:organization/auth/",
    component: BasicLayout,
    meta: { title: "Auth", icon: "view_compact", group: "auth" },
    children: [
      {
        path: "login",
        name: "BasicLogin",
        component: () => import(/* webpackChunkName: "auth-login" */ "@/auth/Login.vue"),
      },
      {
        path: "register",
        name: "BasicRegister",
        component: () => import(/* webpackChunkName: "auth-register" */ "@/auth/Register.vue"),
      },
    ],
  },
  {
    path: "/404",
    name: "404",
    meta: { title: "Not Found" },
    component: () => import(/* webpackChunkName: "errors-404" */ "@/views/error/NotFound.vue"),
  },
  {
    path: "/500",
    name: "500",
    meta: { title: "Server Error" },
    component: () => import(/* webpackChunkName: "errors-500" */ "@/views/error/Error.vue"),
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
      name: "IncidentOverview",
      params: { organization: "default" },
    },
  },
  ...withPrefix("/:organization/", [
    {
      path: "cases/status",
      name: "caseStatus",
      meta: { title: "Case Status", requiresAuth: true },
      component: () => import(/* webpackChunkName: "case-table" */ "@/case/Status.vue"),
    },
    {
      path: "cases/report",
      name: "caseReport",
      meta: { title: "Case Report", requiresAuth: true },
      component: () => import(/* webpackChunkName: "case-report" */ "@/case/ReportForm.vue"),
    },
    {
      path: "incidents/status",
      name: "status",
      meta: { title: "Incident Status", requiresAuth: true },
      component: () => import(/* webpackChunkName: "incident-table" */ "@/incident/Status.vue"),
    },
    {
      path: "incidents/report",
      name: "report",
      meta: { title: "Report", requiresAuth: true },
      component: () =>
        import(/* webpackChunkName: "incidents-report" */ "@/incident/ReportForm.vue"),
    },
    {
      path: "dashboards",
      component: DashboardLayout,
      name: "dashboards",
      redirect: { name: "CaseOverview" },
      meta: {
        title: "Dashboards",
        group: "dashboard",
        icon: "mdi-monitor-dashboard",
        menu: true,
        requiresAuth: true,
      },
      children: [
        {
          path: "cases",
          name: "CaseOverview",
          meta: { title: "Cases", group: "type" },
          component: () =>
            import(/* webpackChunkName: "case-overview" */ "@/dashboard/case/CaseOverview.vue"),
        },
        {
          path: "incidents",
          name: "IncidentOverview",
          meta: { title: "Incidents", group: "type" },
          component: () =>
            import(
              /* webpackChunkName: "incident-overview" */ "@/dashboard/incident/IncidentOverview.vue"
            ),
        },
        {
          path: "tasks",
          name: "TaskOverview",
          meta: { title: "Tasks", group: "type" },
          component: () =>
            import(/* webpackChunkName: "task-overview" */ "@/dashboard/task/TaskOverview.vue"),
        },
        {
          path: "data",
          name: "DataOverview",
          meta: { title: "Data", group: "type" },
          component: () =>
            import(/* webpackChunkName: "data-overview" */ "@/dashboard/data/DataOverview.vue"),
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
          component: () => import(/* webpackChunkName: "incident-table" */ "@/incident/Table.vue"),
          children: [
            {
              path: "/:organization/incidents/:name",
              name: "IncidentTableEdit",
              component: () =>
                import(/* webpackChunkName: "incident-table" */ "@/incident/EditSheet.vue"),
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
          component: () => import(/* webpackChunkName: "case-table" */ "@/case/Table.vue"),
          children: [
            {
              path: "/:organization/cases/:name",
              name: "CaseTableEdit",
              component: () => import(/* webpackChunkName: "case-table" */ "@/case/EditSheet.vue"),
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
      redirect: { name: "SignalTable" },
      children: [
        {
          path: "/:organization/signals",
          name: "SignalTable",
          meta: { title: "List" },
          component: () => import(/* webpackChunkName: "signal-table" */ "@/signal/Table.vue"),
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
          component: () => import(/* webpackChunkName: "source-table" */ "@/data/source/Table.vue"),
        },
        {
          path: "/:organization/data/sources/:name/:tab",
          name: "SourceDetail",
          meta: { title: "Source Detail" },
          component: () =>
            import(/* webpackChunkName: "source-table" */ "@/data/source/Detail.vue"),
        },
        {
          path: "/:organization/data/queries",
          name: "QueryTable",
          meta: { title: "Queries", group: "data" },
          component: () => import(/* webpackChunkName: "query-table" */ "@/data/query/Table.vue"),
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
          component: () => import(/* webpackChunkName: "task-table" */ "@/task/Table.vue"),
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
          component: () => import(/* webpackChunkName: "feedback-table" */ "@/feedback/Table.vue"),
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
          component: () => import(/* webpackChunkName: "projects-table" */ "@/project/Table.vue"),
        },
        {
          path: "members",
          name: "OrganizationMemberTable",
          meta: { title: "Members", subMenu: "organization", group: "organization" },
          component: () =>
            import(
              /* webpackChunkName: "users-table" */ "@/organization/OrganizationMemberTable.vue"
            ),
        },
        {
          path: "projects",
          meta: {
            title: "Project Settings",
            group: "settings",
          },
          name: "ProjectSettings",
          redirect: { name: "CaseTypeTable" },
        },
        ...withPrefix("projects/", [
          {
            path: "plugins",
            name: "PluginTable",
            meta: { title: "Plugins", subMenu: "project", group: "general" },
            component: () => import(/* webpackChunkName: "plugin-table" */ "@/plugin/Table.vue"),
          },
          {
            path: "notifications",
            name: "NotificationTable",
            meta: { title: "Notifications", subMenu: "project", group: "general" },
            component: () =>
              import(/* webpackChunkName: "notification-table" */ "@/notification/Table.vue"),
          },
          {
            path: "workflows",
            name: "WorkflowTable",
            meta: { title: "Workflows", subMenu: "project", group: "general" },
            component: () =>
              import(/* webpackChunkName: "workflows-table" */ "@/workflow/Table.vue"),
          },
          {
            path: "signalSuppressionRules",
            name: "signalSuppressionTable",
            meta: { title: "Suppression Rules", subMenu: "project", group: "signal" },
            component: () =>
              import(
                /* webpackChunkName: "signal-suppression-rule-table" */ "@/signal/suppression_rule/Table.vue"
              ),
          },
          {
            path: "signalDuplicationRules",
            name: "signalDuplicationTable",
            meta: { title: "Duplication Rules", subMenu: "project", group: "signal" },
            component: () =>
              import(
                /* webpackChunkName: "signal-duplication-rule-table" */ "@/signal/duplication_rule/Table.vue"
              ),
          },
          {
            path: "caseTypes",
            name: "CaseTypeTable",
            meta: { title: "Types", subMenu: "project", group: "case" },
            component: () =>
              import(/* webpackChunkName: "case-type-table" */ "@/case/type/Table.vue"),
          },
          {
            path: "caseSeverities",
            name: "caseSeverityTable",
            meta: { title: "Severities", subMenu: "project", group: "case" },
            component: () =>
              import(/* webpackChunkName: "case-severity-table" */ "@/case/severity/Table.vue"),
          },
          {
            path: "casePriorities",
            name: "casePriorityTable",
            meta: { title: "Priorities", subMenu: "project", group: "case" },
            component: () =>
              import(/* webpackChunkName: "case-priority-table" */ "@/case/priority/Table.vue"),
          },
          {
            path: "incidentTypes",
            name: "IncidentTypeTable",
            meta: { title: "Types", subMenu: "project", group: "incident" },
            component: () =>
              import(/* webpackChunkName: "incident-type-table" */ "@/incident_type/Table.vue"),
          },
          {
            path: "incidentPriorities",
            name: "IncidentPriorityTable",
            meta: { title: "Priorities", subMenu: "project", group: "incident" },
            component: () =>
              import(
                /* webpackChunkName: "incident-priority-table" */ "@/incident_priority/Table.vue"
              ),
          },
          {
            path: "incidentCostTypes",
            name: "IncidentCostTypesTable",
            meta: { title: "Cost Types", subMenu: "project", group: "incident" },
            component: () =>
              import(
                /* webpackChunkName: "incident-cost-type-table" */ "@/incident_cost_type/Table.vue"
              ),
          },
          {
            path: "incidentRoles",
            name: "IncidentRolesTable",
            meta: { title: "Roles", subMenu: "project", group: "incident" },
            component: () =>
              import(
                /* webpackChunkName: "incident-cost-type-table" */ "@/incident_role/Table.vue"
              ),
          },
          {
            path: "templates",
            name: "TemplateTable",
            meta: { title: "Templates", subMenu: "project", group: "documentation" },
            component: () =>
              import(
                /* webpackChunkName: "template-table" */ "@/document/template/TemplateTable.vue"
              ),
          },
          {
            path: "references",
            name: "ReferenceTable",
            meta: { title: "References", subMenu: "project", group: "documentation" },
            component: () =>
              import(
                /* webpackChunkName: "reference-table" */ "@/document/reference/ReferenceTable.vue"
              ),
          },
          {
            path: "services",
            name: "ServiceTable",
            meta: { title: "Services", subMenu: "project", group: "contact" },
            component: () => import(/* webpackChunkName: "service-table" */ "@/service/Table.vue"),
          },
          {
            path: "individuals",
            name: "IndividualTable",
            meta: { title: "Individuals", subMenu: "project", group: "contact" },
            component: () =>
              import(/* webpackChunkName: "individual-table" */ "@/individual/Table.vue"),
          },
          {
            path: "teams",
            name: "TeamTable",
            meta: { title: "Teams", subMenu: "project", group: "contact" },
            component: () => import(/* webpackChunkName: "team-table" */ "@/team/Table.vue"),
          },
          {
            path: "tagTypes",
            name: "TagTypeTable",
            meta: { title: "Tag Types", subMenu: "project", group: "knowledge" },
            component: () =>
              import(/* webpackChunkName: "tag-type-table" */ "@/tag_type/Table.vue"),
          },
          {
            path: "tags",
            name: "TagTable",
            meta: { title: "Tags", subMenu: "project", group: "knowledge" },
            component: () => import(/* webpackChunkName: "tag-table" */ "@/tag/Table.vue"),
          },
          {
            path: "runbooks",
            name: "RunbookTable",
            meta: { title: "Runbooks", subMenu: "project", group: "knowledge" },
            component: () =>
              import(
                /* webpackChunkName: "runbooks-table" */ "@/document/runbook/RunbookTable.vue"
              ),
          },
          {
            path: "definitions",
            name: "DefinitionTable",
            meta: { title: "Definitions", subMenu: "project", group: "knowledge" },
            component: () =>
              import(/* webpackchunkname: "definition-table" */ "@/definition/Table.vue"),
          },
          {
            path: "terms",
            name: "TermTable",
            meta: { title: "Terms", subMenu: "project", group: "knowledge" },
            component: () => import(/* webpackChunkName: "term-table" */ "@/term/Table.vue"),
          },
          {
            path: "source/types",
            name: "SourceTypeTable",
            meta: { title: "Source Types", subMenu: "project", group: "data" },
            component: () =>
              import(/* webpackChunkName: "source-type-table" */ "@/data/source/type/Table.vue"),
          },
          {
            path: "source/environments",
            name: "SourceEnvironmentTable",
            meta: { title: "Source Environments", subMenu: "project", group: "data" },
            component: () =>
              import(
                /* webpackChunkName: "environment-table" */ "@/data/source/environment/Table.vue"
              ),
          },
          {
            path: "source/statuses",
            name: "SourceStatusTable",
            meta: { title: "Source Statuses", subMenu: "project", group: "data" },
            component: () =>
              import(/* webpackChunkName: "status-table" */ "@/data/source/status/Table.vue"),
          },
          {
            path: "source/transports",
            name: "SourceTransportTable",
            meta: { title: "Source Transports", subMenu: "project", group: "data" },
            component: () =>
              import(/* webpackchunkname: "transport-table" */ "@/data/source/transport/Table.vue"),
          },
          {
            path: "source/dataFormats",
            name: "SourceDataFormatTable",
            meta: { title: "Source Data Formats", subMenu: "project", group: "data" },
            component: () =>
              import(
                /* webpackChunkName: "dataFormat-table" */ "@/data/source/dataFormat/Table.vue"
              ),
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
          component: () =>
            import(/* webpackChunkName: "search-result-list" */ "@/search/ResultList.vue"),
        },
      ],
    },
  ]),
]
