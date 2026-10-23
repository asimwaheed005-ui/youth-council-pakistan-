import legacyEvents from "./legacy-events.json";
import {documents,publishedDate,wordpressRoutes} from './wordpress';
export const programs = [
 {slug:"leadership-development",title:"Leadership & skill development",category:"Leadership",image:"leadership.jpg",description:"Build the confidence, practical skills, and perspective to lead change in your community.",icon:"leadership"},
 {slug:"climate-action",title:"Climate action & sustainability",category:"Climate",image:"climate.jpg",description:"Bring young voices into the conversations shaping a more sustainable Pakistan.",icon:"climate"},
 {slug:"youth-diplomacy",title:"Youth diplomacy & dialogue",category:"Diplomacy",image:"dialogue.jpg",description:"Connect across cultures, exchange ideas, and explore the world through meaningful dialogue.",icon:"diplomacy"},
 {slug:"education-research",title:"Education & research",category:"Education",image:"community.jpg",description:"Turn curiosity into informed action through learning, research, and knowledge exchange.",icon:"education"}
];
export type EventPhoto={image:string,title:string,description:string,originalCaption:string,sourceUrl:string};
export type ArchiveEvent={slug:string,title:string,originalTitle:string,scope:"domestic"|"international",category:string,city:string,fullDate:string,date:string,month:string,format:string,image:string,description:string,paragraphs:string[],photos:EventPhoto[],sourceUrl:string,sourcePublishedAt:string|null,contentStatus:string,captionSourceUrl?:string};
export const events=legacyEvents as ArchiveEvent[];
export const eventPath=(event:ArchiveEvent)=>`/events/${event.scope}/${event.slug}`;
export const conference=events.find(e=>e.slug==="9th-asia-pacific-climate-change-adaptation-forum-apan")!;
export const conferencePath=eventPath(conference);
export const conferencePhotos=conference.photos;
export const articles=documents.filter(d=>d.kind==='post').map(d=>({...d,date:publishedDate(d.publishedAt),image:d.image.replace(/^\/images\//,'')}));
export const roles = ["Super Admin","Event Manager","Blog Writer","Blog Editor","Registration Manager"];
export const publicPaths = ["about","leadership","leadership/president","members","representatives","programs","events","gallery","news","blog","blog/category/climate","conferences","impact","media","join","contact","faq","search","privacy","terms",...programs.map(x=>`programs/${x.slug}`),...events.flatMap(x=>[`events/${x.slug}`,`events/${x.slug}/register`,eventPath(x).slice(1),`${eventPath(x).slice(1)}/gallery`]),...articles.flatMap(x=>[`blog/${x.slug}`,`news/${x.slug}`]),"gallery/ycp-in-focus","conferences/youth-dialogue-preview"];
export const adminSections=["dashboard","events","programs","registrations","forms","blog","categories","announcements","gallery","conferences","leaders","representatives","impact","notifications","analytics","users","roles","audit-logs","settings"];
export const paths=[...new Set([...publicPaths,...wordpressRoutes,"blog/youth-as-agents-of-change","blog/climate-and-our-future","blog/connecting-beyond-borders","news/youth-as-agents-of-change","news/climate-and-our-future","news/connecting-beyond-borders","events/domestic","events/international","events/international/international-youth-dialogue","events/international/international-youth-dialogue/gallery","admin/login",...adminSections.map(x=>`admin/${x}`),"admin/events/new","admin/blog/new","admin/forms/new","admin/events/sample/edit","admin/blog/sample/edit","admin/forms/sample/edit","admin/registrations/YCP-DEMO-001"])];
