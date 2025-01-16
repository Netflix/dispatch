"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[815],{5680:(e,t,n)=>{n.d(t,{xA:()=>l,yg:()=>u});var r=n(6540);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var c=r.createContext({}),p=function(e){var t=r.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},l=function(e){var t=p(e.components);return r.createElement(c.Provider,{value:t},e.children)},g="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},y=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,o=e.originalType,c=e.parentName,l=s(e,["components","mdxType","originalType","parentName"]),g=p(n),y=a,u=g["".concat(c,".").concat(y)]||g[y]||d[y]||o;return n?r.createElement(u,i(i({ref:t},l),{},{components:n})):r.createElement(u,i({ref:t},l))}));function u(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var o=n.length,i=new Array(o);i[0]=y;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[g]="string"==typeof e?e:a,i[1]=s;for(var p=2;p<o;p++)i[p]=n[p];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}y.displayName="MDXCreateElement"},2236:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>i,default:()=>d,frontMatter:()=>o,metadata:()=>s,toc:()=>p});var r=n(8168),a=(n(6540),n(5680));const o={},i="Tag Types",s={unversionedId:"administration/settings/knowledge/tag-type",id:"administration/settings/knowledge/tag-type",title:"Tag Types",description:"Within Dispatch, tag types are a way to categorize collections of tags (e.g. actor, action, asset, result, etc.).",source:"@site/docs/administration/settings/knowledge/tag-type.mdx",sourceDirName:"administration/settings/knowledge",slug:"/administration/settings/knowledge/tag-type",permalink:"/dispatch/docs/administration/settings/knowledge/tag-type",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/main/docs/docs/administration/settings/knowledge/tag-type.mdx",tags:[],version:"current",frontMatter:{},sidebar:"adminSidebar",previous:{title:"Runbooks",permalink:"/dispatch/docs/administration/settings/knowledge/runbooks"},next:{title:"Tags",permalink:"/dispatch/docs/administration/settings/knowledge/tag"}},c={},p=[],l={toc:p},g="wrapper";function d(e){let{components:t,...o}=e;return(0,a.yg)(g,(0,r.A)({},l,o,{components:t,mdxType:"MDXLayout"}),(0,a.yg)("h1",{id:"tag-types"},"Tag Types"),(0,a.yg)("p",null,"Within Dispatch, tag types are a way to categorize collections of tags (e.g. actor, action, asset, result, etc.)."),(0,a.yg)("div",{style:{textAlign:"center"}},(0,a.yg)("p",null,(0,a.yg)("img",{src:n(3209).A,width:"756",height:"782"}))),(0,a.yg)("p",null,(0,a.yg)("strong",{parentName:"p"},"Name:")," The name for the tag type."),(0,a.yg)("p",null,(0,a.yg)("strong",{parentName:"p"},"Description:")," A short description of the tag type."),(0,a.yg)("p",null,(0,a.yg)("strong",{parentName:"p"},"Exclusive:")," Whether an incident should only have a tag of this type or not."))}d.isMDXComponent=!0},3209:(e,t,n)=>{n.d(t,{A:()=>r});const r=n.p+"assets/images/admin-ui-knowledge-tag-types-6d8f9bd14d5b1eb3b7baa70f2765d54b.png"}}]);