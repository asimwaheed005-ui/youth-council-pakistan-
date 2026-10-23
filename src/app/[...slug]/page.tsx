import Website from "@/components/website";
import {paths,events} from "@/lib/data";
import {sourceDocument,sourceRoute} from '@/lib/wordpress';
export const dynamicParams = false;
export function generateStaticParams(){return paths.map(path=>({slug:path.split("/")}))}
export async function generateMetadata({params}:{params:Promise<{slug:string[]}>}){const {slug}=await params;const event=slug[0]==="events"?events.find(e=>slug.includes(e.slug)):undefined;if(event)return {title:`${event.title}${slug[slug.length-1]==="gallery"?" — Gallery":""}`,description:event.description};const doc=sourceDocument(slug.join('/')==='leadership/president'?'presidents-message':slug[slug.length-1]);if(doc)return {title:doc.title,description:doc.excerpt,alternates:{canonical:sourceRoute(doc)},robots:slug[0]==='source-archive'||['team','donor-dashboard','donation-failed','donation-confirmation'].includes(doc.slug)?{index:false,follow:true}:undefined};const label=slug[slug.length-1].replaceAll("-"," ");return {title:label.charAt(0).toUpperCase()+label.slice(1)}}
export default async function Page({params}:{params:Promise<{slug:string[]}>}){const {slug}=await params;return <Website path={slug.join("/")}/>}
