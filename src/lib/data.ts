export const programs = [
 {slug:"leadership-development",title:"Leadership & skill development",category:"Leadership",image:"leadership.jpg",description:"Build the confidence, practical skills, and perspective to lead change in your community.",icon:"leadership"},
 {slug:"climate-action",title:"Climate action & sustainability",category:"Climate",image:"climate.jpg",description:"Bring young voices into the conversations shaping a more sustainable Pakistan.",icon:"climate"},
 {slug:"youth-diplomacy",title:"Youth diplomacy & dialogue",category:"Diplomacy",image:"dialogue.jpg",description:"Connect across cultures, exchange ideas, and explore the world through meaningful dialogue.",icon:"diplomacy"},
 {slug:"education-research",title:"Education & research",category:"Education",image:"community.jpg",description:"Turn curiosity into informed action through learning, research, and knowledge exchange.",icon:"education"}
];
export const events = [
 {slug:"youth-leadership-dialogue",title:"Youth Leadership Dialogue",category:"Leadership",city:"Islamabad",date:"14",month:"NOV",fullDate:"14 November 2026",format:"In person",image:"leadership.jpg",description:"An illustrative gathering for young people to explore leadership, community participation, and purposeful action."},
 {slug:"climate-action-roundtable",title:"Climate Action Roundtable",category:"Climate",city:"Lahore",date:"21",month:"NOV",fullDate:"21 November 2026",format:"Hybrid",image:"climate.jpg",description:"An illustrative roundtable bringing youth perspectives to climate challenges and local solutions."},
 {slug:"global-youth-connections",title:"Global Youth Connections",category:"Diplomacy",city:"Online",date:"05",month:"DEC",fullDate:"5 December 2026",format:"Online",image:"dialogue.jpg",description:"An illustrative online exchange exploring collaboration, cultural understanding, and youth diplomacy."}
];
export const articles = [
 {slug:"youth-as-agents-of-change",title:"From participants to changemakers: putting youth at the center",category:"Youth development",image:"leadership.jpg",date:"Editorial preview",excerpt:"Exploring how meaningful participation can help young people shape the communities they belong to."},
 {slug:"climate-and-our-future",title:"The future of climate action starts with young voices",category:"Climate",image:"climate.jpg",date:"Editorial preview",excerpt:"Why education, dialogue, and local participation belong at the heart of the climate conversation."},
 {slug:"connecting-beyond-borders",title:"Connecting beyond borders through youth diplomacy",category:"International relations",image:"community.jpg",date:"Editorial preview",excerpt:"A closer look at the value of exchange, shared learning, and connections across cultures."}
];
export const roles = ["Super Admin","Event Manager","Blog Writer","Blog Editor","Registration Manager"];
export const publicPaths = ["about","leadership","leadership/president","members","representatives","programs","events","gallery","news","blog","blog/category/climate","conferences","impact","media","join","contact","faq","search","privacy","terms",...programs.map(x=>`programs/${x.slug}`),...events.flatMap(x=>[`events/${x.slug}`,`events/${x.slug}/register`]),...articles.flatMap(x=>[`blog/${x.slug}`,`news/${x.slug}`]),"gallery/ycp-in-focus","conferences/youth-dialogue-preview"];
export const adminSections=["dashboard","events","programs","registrations","forms","blog","categories","announcements","gallery","conferences","leaders","representatives","impact","notifications","analytics","users","roles","audit-logs","settings"];
export const paths=[...publicPaths,"admin/login",...adminSections.map(x=>`admin/${x}`),"admin/events/new","admin/blog/new","admin/forms/new","admin/events/sample/edit","admin/blog/sample/edit","admin/forms/sample/edit","admin/registrations/YCP-DEMO-001"];
