import Website from "@/components/website";
import {paths} from "@/lib/data";
export const dynamicParams = false;
export function generateStaticParams(){return paths.map(path=>({slug:path.split("/")}))}
export async function generateMetadata({params}:{params:Promise<{slug:string[]}>}){const {slug}=await params;const label=slug[slug.length-1].replaceAll("-"," ");return {title:label.charAt(0).toUpperCase()+label.slice(1)}}
export default async function Page({params}:{params:Promise<{slug:string[]}>}){const {slug}=await params;return <Website path={slug.join("/")}/>}
