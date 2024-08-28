"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[211],{5680:(e,t,n)=>{n.d(t,{xA:()=>u,yg:()=>m});var r=n(6540);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function a(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,i=function(e,t){if(null==e)return{};var n,r,i={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var l=r.createContext({}),c=function(e){var t=r.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):a(a({},t),e)),n},u=function(e){var t=c(e.components);return r.createElement(l.Provider,{value:t},e.children)},d="mdxType",p={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},g=r.forwardRef((function(e,t){var n=e.components,i=e.mdxType,o=e.originalType,l=e.parentName,u=s(e,["components","mdxType","originalType","parentName"]),d=c(n),g=i,m=d["".concat(l,".").concat(g)]||d[g]||p[g]||o;return n?r.createElement(m,a(a({ref:t},u),{},{components:n})):r.createElement(m,a({ref:t},u))}));function m(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var o=n.length,a=new Array(o);a[0]=g;var s={};for(var l in t)hasOwnProperty.call(t,l)&&(s[l]=t[l]);s.originalType=e,s[d]="string"==typeof e?e:i,a[1]=s;for(var c=2;c<o;c++)a[c]=n[c];return r.createElement.apply(null,a)}return r.createElement.apply(null,n)}g.displayName="MDXCreateElement"},1310:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>a,default:()=>p,frontMatter:()=>o,metadata:()=>s,toc:()=>c});var r=n(8168),i=(n(6540),n(5680));const o={},a="Runbooks",s={unversionedId:"administration/settings/knowledge/runbooks",id:"administration/settings/knowledge/runbooks",title:"Runbooks",description:"Runbooks allow for Dispatch users to provide documents dynamically to incident participants that may be useful during an incident.",source:"@site/docs/administration/settings/knowledge/runbooks.mdx",sourceDirName:"administration/settings/knowledge",slug:"/administration/settings/knowledge/runbooks",permalink:"/dispatch/docs/administration/settings/knowledge/runbooks",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/administration/settings/knowledge/runbooks.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Definitions",permalink:"/dispatch/docs/administration/settings/knowledge/definition"},next:{title:"Tag Types",permalink:"/dispatch/docs/administration/settings/knowledge/tag-type"}},l={},c=[{value:"Engagement",id:"engagement",level:3},{value:"Evergreen",id:"evergreen",level:3}],u={toc:c},d="wrapper";function p(e){let{components:t,...o}=e;return(0,i.yg)(d,(0,r.A)({},u,o,{components:t,mdxType:"MDXLayout"}),(0,i.yg)("h1",{id:"runbooks"},"Runbooks"),(0,i.yg)("p",null,"Runbooks allow for Dispatch users to provide documents dynamically to incident participants that may be useful during an incident."),(0,i.yg)("p",null,"Where templates are used to document the state of the incident runbooks typically document steps to take to resolve an incident."),(0,i.yg)("p",null,"How closely these two ideas are related depends on the incident and how your organization runs it's incidents."),(0,i.yg)("p",null,"Today, there are two types of runbooks although their actual usage is the same."),(0,i.yg)("ul",null,(0,i.yg)("li",{parentName:"ul"},"Incident"),(0,i.yg)("li",{parentName:"ul"},"Investigation")),(0,i.yg)("h3",{id:"engagement"},"Engagement"),(0,i.yg)("p",null,"Runbook documents are dymanically matched to an incident based on their engagement filter. Similar to notification's a user can define for which incidents a document should be recommended to incident participants."),(0,i.yg)("p",null,"On incident creation (or when an important incident variable changes e.g. incident type) Dispatch will send the incident channel a document suggestion notification."),(0,i.yg)("div",{style:{textAlign:"center"}},(0,i.yg)("p",null,(0,i.yg)("img",{src:n(1748).A,width:"499",height:"1003"}))),(0,i.yg)("p",null,(0,i.yg)("strong",{parentName:"p"},"Name:")," Name of the document."),(0,i.yg)("p",null,(0,i.yg)("strong",{parentName:"p"},"Description:")," Short description of the document."),(0,i.yg)("p",null,(0,i.yg)("strong",{parentName:"p"},"Weblink:")," A hyperlink representing the document."),(0,i.yg)("p",null,(0,i.yg)("strong",{parentName:"p"},"ID:")," The external ID that is used to fetch the document."),(0,i.yg)("h3",{id:"evergreen"},"Evergreen"),(0,i.yg)("p",null,"Enabling evergreen for a runbook instructs Dispatch to send an email reminder to the runbook owner, informing them that they should check to ensure that the runbook in question is up to date."))}p.isMDXComponent=!0},1748:(e,t,n)=>{n.d(t,{A:()=>r});const r=n.p+"assets/images/admin-ui-create-edit-runbook-a3004a8880b5a98ea4070e2ae943142f.png"}}]);