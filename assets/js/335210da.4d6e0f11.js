"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[9606],{5680:(e,t,n)=>{n.d(t,{xA:()=>u,yg:()=>f});var i=n(6540);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,i)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,i,r=function(e,t){if(null==e)return{};var n,i,r={},a=Object.keys(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var c=i.createContext({}),l=function(e){var t=i.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},u=function(e){var t=l(e.components);return i.createElement(c.Provider,{value:t},e.children)},p="mdxType",g={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},d=i.forwardRef((function(e,t){var n=e.components,r=e.mdxType,a=e.originalType,c=e.parentName,u=s(e,["components","mdxType","originalType","parentName"]),p=l(n),d=r,f=p["".concat(c,".").concat(d)]||p[d]||g[d]||a;return n?i.createElement(f,o(o({ref:t},u),{},{components:n})):i.createElement(f,o({ref:t},u))}));function f(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var a=n.length,o=new Array(a);o[0]=d;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[p]="string"==typeof e?e:r,o[1]=s;for(var l=2;l<a;l++)o[l]=n[l];return i.createElement.apply(null,o)}return i.createElement.apply(null,n)}d.displayName="MDXCreateElement"},9533:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>o,default:()=>g,frontMatter:()=>a,metadata:()=>s,toc:()=>l});var i=n(8168),r=(n(6540),n(5680));const a={},o="Plugins",s={unversionedId:"administration/settings/plugins/index",id:"administration/settings/plugins/index",title:"Plugins",description:"Before being able to configure and use the plugins, refer to the CLI documentation about installing plugins.",source:"@site/docs/administration/settings/plugins/index.mdx",sourceDirName:"administration/settings/plugins",slug:"/administration/settings/plugins/",permalink:"/dispatch/docs/administration/settings/plugins/",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/main/docs/docs/administration/settings/plugins/index.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Messaging",permalink:"/dispatch/docs/administration/settings/messaging"},next:{title:"Configuring Atlassian Confluence",permalink:"/dispatch/docs/administration/settings/plugins/configuring-atlassian-confluence"}},c={},l=[],u={toc:l},p="wrapper";function g(e){let{components:t,...a}=e;return(0,r.yg)(p,(0,i.A)({},u,a,{components:t,mdxType:"MDXLayout"}),(0,r.yg)("h1",{id:"plugins"},"Plugins"),(0,r.yg)("p",null,"Before being able to configure and use the plugins, refer to the ",(0,r.yg)("a",{parentName:"p",href:"/dispatch/docs/administration/cli#plugins"},"CLI")," documentation about installing plugins."),(0,r.yg)("p",null,"Much of Dispatch's functionality comes from its plugins. The current Dispatch web UI is limited to enabling and disabling plugins on a per-project basis. To make modifications to how plugins behave or are configured, changes must be deployed via the server configuration file. See the ",(0,r.yg)("a",{parentName:"p",href:"/dispatch/docs/administration/settings/server"},"server")," configuration documentation for more information."),(0,r.yg)("p",null,"By default, no plugins are ",(0,r.yg)("em",{parentName:"p"},"required")," to create an incident. As you enable plugins, they will be additive to the incident process (e.g., creating slack channels, google docs, etc.)"),(0,r.yg)("div",{style:{textAlign:"center"}},(0,r.yg)("p",null,(0,r.yg)("img",{src:n(8893).A,width:"492",height:"626"}))),(0,r.yg)("p",null,"Looking to add your own functionality to Dispatch via plugins? See the ",(0,r.yg)("a",{parentName:"p",href:"/dispatch/docs/administration/contributing/plugins/"},"contributing")," documentation."))}g.isMDXComponent=!0},8893:(e,t,n)=>{n.d(t,{A:()=>i});const i=n.p+"assets/images/admin-ui-incident-plugins-583f6c7406f9cc4e8994ccaf7885f9ab.png"}}]);