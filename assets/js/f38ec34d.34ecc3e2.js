"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[1241],{5680:(e,t,n)=>{n.d(t,{xA:()=>d,yg:()=>g});var i=n(6540);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function r(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,i)}return n}function a(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?r(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,i,o=function(e,t){if(null==e)return{};var n,i,o={},r=Object.keys(e);for(i=0;i<r.length;i++)n=r[i],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(i=0;i<r.length;i++)n=r[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var c=i.createContext({}),p=function(e){var t=i.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):a(a({},t),e)),n},d=function(e){var t=p(e.components);return i.createElement(c.Provider,{value:t},e.children)},l="mdxType",y={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},u=i.forwardRef((function(e,t){var n=e.components,o=e.mdxType,r=e.originalType,c=e.parentName,d=s(e,["components","mdxType","originalType","parentName"]),l=p(n),u=o,g=l["".concat(c,".").concat(u)]||l[u]||y[u]||r;return n?i.createElement(g,a(a({ref:t},d),{},{components:n})):i.createElement(g,a({ref:t},d))}));function g(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var r=n.length,a=new Array(r);a[0]=u;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[l]="string"==typeof e?e:o,a[1]=s;for(var p=2;p<r;p++)a[p]=n[p];return i.createElement.apply(null,a)}return i.createElement.apply(null,n)}u.displayName="MDXCreateElement"},3962:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>a,default:()=>y,frontMatter:()=>r,metadata:()=>s,toc:()=>p});var i=n(8168),o=(n(6540),n(5680));const r={},a="Incident Types",s={unversionedId:"administration/settings/incident/incident-type",id:"administration/settings/incident/incident-type",title:"Incident Types",description:"Dispatch allows you to categorize your incidents by defining incidents types and to map them to various Dispatch resources (e.g. templates).",source:"@site/docs/administration/settings/incident/incident-type.mdx",sourceDirName:"administration/settings/incident",slug:"/administration/settings/incident/incident-type",permalink:"/dispatch/docs/administration/settings/incident/incident-type",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/main/docs/docs/administration/settings/incident/incident-type.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Incident Priority",permalink:"/dispatch/docs/administration/settings/incident/incident-priority"},next:{title:"Notification",permalink:"/dispatch/docs/administration/settings/incident/notification"}},c={},p=[],d={toc:p},l="wrapper";function y(e){let{components:t,...r}=e;return(0,o.yg)(l,(0,i.A)({},d,r,{components:t,mdxType:"MDXLayout"}),(0,o.yg)("h1",{id:"incident-types"},"Incident Types"),(0,o.yg)("p",null,"Dispatch allows you to categorize your incidents by defining incidents types and to map them to various Dispatch resources (e.g. templates)."),(0,o.yg)("div",{style:{textAlign:"center"}},(0,o.yg)("p",null,(0,o.yg)("img",{src:n(6034).A,width:"786",height:"1666"}))),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Name:")," The name of the incident type presented to the user."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Description:")," The description of the incident type presented to the user."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Visibility:")," Allows you to specify how visible an incident of this type will be. For example, if ",(0,o.yg)("inlineCode",{parentName:"p"},"Open")," is chosen, then notifications about an incident of this type will be sent on incident creation and update, and updates included on daily incident reports. All Dispatch users will be able to see incidents of this type in the Web UI regardless of their role. Also, Dispatch will use the Google domain provided to add organization-wide permission to the incident folder and its contents when the incident is marked as closed. However, if ",(0,o.yg)("inlineCode",{parentName:"p"},"Restricted")," is chosen, incidents of this type will not be included in notifications, won't be visible to Dispatch users with a ",(0,o.yg)("inlineCode",{parentName:"p"},"member")," role in the Web UI, and Dispatch won't open the incident folder and its contents to the whole organization. This setting defaults to ",(0,o.yg)("inlineCode",{parentName:"p"},"Open"),"."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Incident Template:")," Allows you to create a new or map an existing incident document template to the incident type."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Executive Template:")," Allows you to create a new or map an existing executive report document template to the incident type."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Review Template:")," Allows you to create a new or map an existing post-incident review document template to the incident type."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Tracking Template:")," Allows you to create a new or map an existing incident tracking sheet template to the incident type."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Exclude From Metrics:"),' Enable this setting to exclude all incidents of this type from metrics (e.g., "Simulation" or "Test" incidents).'),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Default Incident Type:")," If the reporter of an incident does not provide an incident type, a default incident type is used. Enable this setting to make this incident type the default."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Enabled:")," Whether the incident type is enabled or not."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Plugin Metadata:")," Allows you to define and pass metadata key-value pairs to plugins. For example, create issues in different Jira projects based on the incident type."),(0,o.yg)("p",null,(0,o.yg)("strong",{parentName:"p"},"Cost Model:")," Allows you to define how to calculate incident response costs. If an incident type does not have a cost model assigned, the default classic cost model will be used when calculating the incident costs. See ",(0,o.yg)("a",{parentName:"p",href:"/dispatch/docs/administration/settings/cost_model"},"Cost Model"),"."))}y.isMDXComponent=!0},6034:(e,t,n)=>{n.d(t,{A:()=>i});const i=n.p+"assets/images/admin-ui-incident-types-254ff95675a9bdaaf9aea420dec55c59.png"}}]);