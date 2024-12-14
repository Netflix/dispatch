"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[4431],{5680:(e,t,n)=>{n.d(t,{xA:()=>d,yg:()=>m});var r=n(6540);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},i=Object.keys(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var p=r.createContext({}),l=function(e){var t=r.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},d=function(e){var t=l(e.components);return r.createElement(p.Provider,{value:t},e.children)},g="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},c=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,i=e.originalType,p=e.parentName,d=s(e,["components","mdxType","originalType","parentName"]),g=l(n),c=a,m=g["".concat(p,".").concat(c)]||g[c]||u[c]||i;return n?r.createElement(m,o(o({ref:t},d),{},{components:n})):r.createElement(m,o({ref:t},d))}));function m(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var i=n.length,o=new Array(i);o[0]=c;var s={};for(var p in t)hasOwnProperty.call(t,p)&&(s[p]=t[p]);s.originalType=e,s[g]="string"==typeof e?e:a,o[1]=s;for(var l=2;l<i;l++)o[l]=n[l];return r.createElement.apply(null,o)}return r.createElement.apply(null,n)}c.displayName="MDXCreateElement"},9977:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>o,default:()=>u,frontMatter:()=>i,metadata:()=>s,toc:()=>l});var r=n(8168),a=(n(6540),n(5680));const i={sidebar_position:2,description:"Staying up to date."},o="Upgrading",s={unversionedId:"administration/upgrading",id:"administration/upgrading",title:"Upgrading",description:"Staying up to date.",source:"@site/docs/administration/upgrading.mdx",sourceDirName:"administration",slug:"/administration/upgrading",permalink:"/dispatch/docs/administration/upgrading",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/administration/upgrading.mdx",tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2,description:"Staying up to date."},sidebar:"adminSidebar",previous:{title:"Installation",permalink:"/dispatch/docs/administration/installation"},next:{title:"User Management",permalink:"/dispatch/docs/administration/user"}},p={},l=[{value:"Upgrading Dispatch",id:"upgrading-dispatch",level:2},{value:"Upgrading the package",id:"upgrading-the-package",level:3},{value:"Running Migrations",id:"running-migrations",level:3},{value:"Restarting services",id:"restarting-services",level:3}],d={toc:l},g="wrapper";function u(e){let{components:t,...n}=e;return(0,a.yg)(g,(0,r.A)({},d,n,{components:t,mdxType:"MDXLayout"}),(0,a.yg)("h1",{id:"upgrading"},"Upgrading"),(0,a.yg)("p",null,"If you're upgrading to a new major release, you should generate a new configuration file using the latest Dispatch version. Doing so ensures that any new settings are visible and configured if required."),(0,a.yg)("p",null,"Beyond that, upgrades are simple as bumping the version of Dispatch ","(","which will cause any changed dependencies to upgrade",")",", running data migrations, and restarting all related services."),(0,a.yg)("admonition",{type:"info"},(0,a.yg)("p",{parentName:"admonition"},"In some cases, you may want to stop services before doing the upgrade process or avoid intermittent errors.")),(0,a.yg)("h2",{id:"upgrading-dispatch"},"Upgrading Dispatch"),(0,a.yg)("h3",{id:"upgrading-the-package"},"Upgrading the package"),(0,a.yg)("p",null,"The easiest way to upgrade the Dispatch package using ",(0,a.yg)("inlineCode",{parentName:"p"},"pip"),":"),(0,a.yg)("pre",null,(0,a.yg)("code",{parentName:"pre",className:"language-bash"},"pip install --upgrade dispatch\n")),(0,a.yg)("p",null,"You may prefer to install a fixed version rather than the latest, as it will allow you to control changes."),(0,a.yg)("p",null,"If you're installing from source code, you may have additional unfulfilled requirements, so take the necessary precautions of testing your environment before committing to the upgrade."),(0,a.yg)("h3",{id:"running-migrations"},"Running Migrations"),(0,a.yg)("p",null,"Just as during the initial setup, migrations are applied with the upgrade command."),(0,a.yg)("pre",null,(0,a.yg)("code",{parentName:"pre",className:"language-bash"},"dispatch database upgrade\n")),(0,a.yg)("h3",{id:"restarting-services"},"Restarting services"),(0,a.yg)("p",null,"You'll need to ensure that ",(0,a.yg)("em",{parentName:"p"},"all")," of Dispatch's services are restarted after an upgrade. Restarting these services is required because Python loads modules in memory, and code changes will not be reflected until they are restarted."),(0,a.yg)("p",null,"These services include:"),(0,a.yg)("ul",null,(0,a.yg)("li",{parentName:"ul"},"server -- ",(0,a.yg)("inlineCode",{parentName:"li"},"dispatch server start")),(0,a.yg)("li",{parentName:"ul"},"scheduler -- ",(0,a.yg)("inlineCode",{parentName:"li"},"dispatch scheduler start"))))}u.isMDXComponent=!0}}]);