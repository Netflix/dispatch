"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[5780],{5680:(e,n,t)=>{t.d(n,{xA:()=>u,yg:()=>f});var i=t(6540);function a(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function r(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);n&&(i=i.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,i)}return t}function o(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?r(Object(t),!0).forEach((function(n){a(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):r(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function s(e,n){if(null==e)return{};var t,i,a=function(e,n){if(null==e)return{};var t,i,a={},r=Object.keys(e);for(i=0;i<r.length;i++)t=r[i],n.indexOf(t)>=0||(a[t]=e[t]);return a}(e,n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(i=0;i<r.length;i++)t=r[i],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(a[t]=e[t])}return a}var l=i.createContext({}),c=function(e){var n=i.useContext(l),t=n;return e&&(t="function"==typeof e?e(n):o(o({},n),e)),t},u=function(e){var n=c(e.components);return i.createElement(l.Provider,{value:n},e.children)},d="mdxType",p={inlineCode:"code",wrapper:function(e){var n=e.children;return i.createElement(i.Fragment,{},n)}},g=i.forwardRef((function(e,n){var t=e.components,a=e.mdxType,r=e.originalType,l=e.parentName,u=s(e,["components","mdxType","originalType","parentName"]),d=c(t),g=a,f=d["".concat(l,".").concat(g)]||d[g]||p[g]||r;return t?i.createElement(f,o(o({ref:n},u),{},{components:t})):i.createElement(f,o({ref:n},u))}));function f(e,n){var t=arguments,a=n&&n.mdxType;if("string"==typeof e||a){var r=t.length,o=new Array(r);o[0]=g;var s={};for(var l in n)hasOwnProperty.call(n,l)&&(s[l]=n[l]);s.originalType=e,s[d]="string"==typeof e?e:a,o[1]=s;for(var c=2;c<r;c++)o[c]=t[c];return i.createElement.apply(null,o)}return i.createElement.apply(null,t)}g.displayName="MDXCreateElement"},7608:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>o,default:()=>p,frontMatter:()=>r,metadata:()=>s,toc:()=>c});var i=t(8168),a=(t(6540),t(5680));const r={description:"Configuration page for Atlassian Confluence."},o="Configuring Atlassian Confluence",s={unversionedId:"administration/settings/plugins/configuring-atlassian-confluence",id:"administration/settings/plugins/configuring-atlassian-confluence",title:"Configuring Atlassian Confluence",description:"Configuration page for Atlassian Confluence.",source:"@site/docs/administration/settings/plugins/configuring-atlassian-confluence.mdx",sourceDirName:"administration/settings/plugins",slug:"/administration/settings/plugins/configuring-atlassian-confluence",permalink:"/dispatch/docs/administration/settings/plugins/configuring-atlassian-confluence",draft:!1,editUrl:"https://github.com/netflix/dispatch/edit/master/docs/docs/administration/settings/plugins/configuring-atlassian-confluence.mdx",tags:[],version:"current",frontMatter:{description:"Configuration page for Atlassian Confluence."},sidebar:"adminSidebar",previous:{title:"Plugins",permalink:"/dispatch/docs/administration/settings/plugins/"},next:{title:"Configuring Duo",permalink:"/dispatch/docs/administration/settings/plugins/configuring-duo"}},l={},c=[{value:"Dispatch configuration variables for storage plugin",id:"dispatch-configuration-variables-for-storage-plugin",level:2},{value:"<code>API URL</code> [Required]",id:"api-url-required",level:3},{value:"<code>Username</code> [Required]",id:"username-required",level:3},{value:"<code>Password</code> [Required]",id:"password-required",level:3},{value:"<code>Incident template ID</code> [Required]",id:"incident-template-id-required",level:3},{value:"<code>Default Space ID</code> [Required]",id:"default-space-id-required",level:3},{value:"<code>Parent ID of the pages</code> [Required]",id:"parent-id-of-the-pages-required",level:3},{value:"Dispatch Configuration Variables for document plugin",id:"dispatch-configuration-variables-for-document-plugin",level:2},{value:"<code>API URL</code> [Required]",id:"api-url-required-1",level:3},{value:"<code>Username</code> [Required]",id:"username-required-1",level:3},{value:"<code>Password</code> [Required]",id:"password-required-1",level:3}],u={toc:c},d="wrapper";function p(e){let{components:n,...t}=e;return(0,a.yg)(d,(0,i.A)({},u,t,{components:n,mdxType:"MDXLayout"}),(0,a.yg)("h1",{id:"configuring-atlassian-confluence"},"Configuring Atlassian Confluence"),(0,a.yg)("admonition",{type:"info"},(0,a.yg)("p",{parentName:"admonition"},"Dispatch ships with Atlassian Confluence storage and document plugins. This page describes the available configurations for the plugins.")),(0,a.yg)("h2",{id:"dispatch-configuration-variables-for-storage-plugin"},"Dispatch configuration variables for storage plugin"),(0,a.yg)("h3",{id:"api-url-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"API URL")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"URL of the confluence cloud instance.")),(0,a.yg)("h3",{id:"username-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"Username")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"Username for accessing the confluence instance. This user should have permission to create pages in the space.")),(0,a.yg)("h3",{id:"password-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"Password")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"API token to access the confluence instance. Please refer to the ",(0,a.yg)("a",{parentName:"p",href:"https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/"},"link")," on creating a new API token.")),(0,a.yg)("h3",{id:"incident-template-id-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"Incident template ID")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"This is the page id of the template that contains the post incident review document details. The plugin uses this template to create a new page and then replace the supported variables with the incident details.")),(0,a.yg)("h3",{id:"default-space-id-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"Default Space ID")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"This is the default space ",(0,a.yg)("a",{parentName:"p",href:"https://confluence.atlassian.com/doc/space-keys-829076188.html"},"key")," where all the pages will be created in confluence.")),(0,a.yg)("h3",{id:"parent-id-of-the-pages-required"},(0,a.yg)("inlineCode",{parentName:"h3"},"Parent ID of the pages")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"This is the page id, where all the new pages and subpages will be created.")),(0,a.yg)("h2",{id:"dispatch-configuration-variables-for-document-plugin"},"Dispatch Configuration Variables for document plugin"),(0,a.yg)("h3",{id:"api-url-required-1"},(0,a.yg)("inlineCode",{parentName:"h3"},"API URL")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"URL of the confluence cloud instance.")),(0,a.yg)("h3",{id:"username-required-1"},(0,a.yg)("inlineCode",{parentName:"h3"},"Username")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"Username for accessing the confluence instance. This user should have permission to create pages in the space.")),(0,a.yg)("h3",{id:"password-required-1"},(0,a.yg)("inlineCode",{parentName:"h3"},"Password")," ","[","Required","]"),(0,a.yg)("blockquote",null,(0,a.yg)("p",{parentName:"blockquote"},"API token to access the confluence instance. Please refer to the ",(0,a.yg)("a",{parentName:"p",href:"https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/"},"link")," on creating a new API token.")))}p.isMDXComponent=!0}}]);