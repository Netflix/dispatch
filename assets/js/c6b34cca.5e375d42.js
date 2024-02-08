"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[1402],{4137:(t,e,n)=>{n.d(e,{Zo:()=>p,kt:()=>f});var r=n(7294);function a(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function o(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(t);e&&(r=r.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,r)}return n}function i(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?o(Object(n),!0).forEach((function(e){a(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}function s(t,e){if(null==t)return{};var n,r,a=function(t,e){if(null==t)return{};var n,r,a={},o=Object.keys(t);for(r=0;r<o.length;r++)n=o[r],e.indexOf(n)>=0||(a[n]=t[n]);return a}(t,e);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);for(r=0;r<o.length;r++)n=o[r],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(t,n)&&(a[n]=t[n])}return a}var c=r.createContext({}),l=function(t){var e=r.useContext(c),n=e;return t&&(n="function"==typeof t?t(e):i(i({},e),t)),n},p=function(t){var e=l(t.components);return r.createElement(c.Provider,{value:e},t.children)},d="mdxType",u={inlineCode:"code",wrapper:function(t){var e=t.children;return r.createElement(r.Fragment,{},e)}},m=r.forwardRef((function(t,e){var n=t.components,a=t.mdxType,o=t.originalType,c=t.parentName,p=s(t,["components","mdxType","originalType","parentName"]),d=l(n),m=a,f=d["".concat(c,".").concat(m)]||d[m]||u[m]||o;return n?r.createElement(f,i(i({ref:e},p),{},{components:n})):r.createElement(f,i({ref:e},p))}));function f(t,e){var n=arguments,a=e&&e.mdxType;if("string"==typeof t||a){var o=n.length,i=new Array(o);i[0]=m;var s={};for(var c in e)hasOwnProperty.call(e,c)&&(s[c]=e[c]);s.originalType=t,s[d]="string"==typeof t?t:a,i[1]=s;for(var l=2;l<o;l++)i[l]=n[l];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}m.displayName="MDXCreateElement"},9285:(t,e,n)=>{n.r(e),n.d(e,{assets:()=>c,contentTitle:()=>i,default:()=>u,frontMatter:()=>o,metadata:()=>s,toc:()=>l});var r=n(7462),a=(n(7294),n(4137));const o={},i="Environment",s={unversionedId:"administration/settings/data/environment",id:"administration/settings/data/environment",title:"Environment",description:"Data sources often have a corresponding environment to which they apply. For example, one data set may only contain information from the production account. When responding to incidents and using data sources for investigation, it's essential to understand the data source's scope.",source:"@site/docs/administration/settings/data/environment.mdx",sourceDirName:"administration/settings/data",slug:"/administration/settings/data/environment",permalink:"/dispatch/docs/administration/settings/data/environment",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/administration/settings/data/environment.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Data Formats",permalink:"/dispatch/docs/administration/settings/data/data-format"},next:{title:"Status",permalink:"/dispatch/docs/administration/settings/data/status"}},c={},l=[],p={toc:l},d="wrapper";function u(t){let{components:e,...n}=t;return(0,a.kt)(d,(0,r.Z)({},p,n,{components:e,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"environment"},"Environment"),(0,a.kt)("p",null,"Data sources often have a corresponding environment to which they apply. For example, one data set may only contain information from the production account. When responding to incidents and using data sources for investigation, it's essential to understand the data source's scope."),(0,a.kt)("p",null,"Some examples of a data source's environment could be:"),(0,a.kt)("ul",null,(0,a.kt)("li",{parentName:"ul"},"Production"),(0,a.kt)("li",{parentName:"ul"},"Staging"),(0,a.kt)("li",{parentName:"ul"},"Testing"),(0,a.kt)("li",{parentName:"ul"},"Development")))}u.isMDXComponent=!0}}]);