import imported from './wordpress-content.json';

export type ContentLink={text:string;href:string};
export type ContentBlock={type:string;text?:string;level?:number;src?:string;alt?:string;caption?:string;href?:string;items?:string[];ordered?:boolean;rows?:string[][];links?:ContentLink[]};
export type WordPressDocument={id:number;slug:string;title:string;sourceUrl:string;kind:string;publishedAt:string;modifiedAt:string;image:string;category:string;categories:string[];excerpt:string;blocks:ContentBlock[];author:string;tags:number[];comments:{author:string;date:string;text:string}[]};
export const documents=imported.documents as WordPressDocument[];
export const wordpressConfig=imported.config;
export const wordpressMedia=imported.media;
export const wordpressCategories=imported.categories;
export const wordpressTags=imported.tags;
export const sourceDocument=(slug:string)=>documents.find(d=>d.slug===slug);
export const publishedDate=(value:string)=>new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(`${value}Z`));
export const primarySourcePaths:Record<string,string>={'home-2':'/','about':'/about','presidents-message':'/leadership/president','blogs':'/blog','events':'/events','contact':'/contact','join-us':'/join','team':'/team'};
export const sourceRoute=(doc:WordPressDocument)=>doc.kind==='post'?`/blog/${doc.slug}`:primarySourcePaths[doc.slug]||`/${doc.slug}`;
export function localSourceLink(href:string){
 if(href.startsWith('mailto:')||href.startsWith('tel:'))return href;
 try{const url=new URL(href);if(url.hostname!=='youthcouncil.pk'&&url.hostname!=='www.youthcouncil.pk')return href;
 const asset=wordpressMedia.find(m=>m.sourceUrl===href);if(asset?.available)return asset.src;
 if(url.pathname==='/')return '/';
 const doc=documents.find(d=>new URL(d.sourceUrl).pathname===url.pathname);if(doc)return `${sourceRoute(doc)}${url.hash}`;
 const category=wordpressCategories.find(c=>url.pathname===`/category/${c.slug}/`);if(category)return `/blog/category/${category.slug}`;
 return href;
 }catch{return href;}
}
export const wordpressRoutes=[...documents.flatMap(d=>[d.slug,`source-archive/${d.slug}`]),...wordpressCategories.flatMap(c=>[`blog/category/${c.slug}`,`category/${c.slug}`]),...wordpressTags.map(t=>`tag/${t.slug}`),'source-archive'];
