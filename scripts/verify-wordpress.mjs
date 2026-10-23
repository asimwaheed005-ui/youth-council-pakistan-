import {chromium,expect} from '@playwright/test';
import {readFile,stat} from 'node:fs/promises';
import assert from 'node:assert/strict';
const imported=JSON.parse(await readFile('src/lib/wordpress-content.json','utf8'));
const report=JSON.parse(await readFile('src/lib/wordpress-migration.json','utf8'));
const origin=process.env.QA_ORIGIN||'http://127.0.0.1:3100';
const normalize=s=>s.replace(/\s+/g,' ').trim();
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 assert.equal(imported.documents.filter(d=>d.kind==='post').length,report.posts);
 assert.equal(imported.documents.filter(d=>d.kind==='page').length,report.pages);
 for(const doc of imported.documents){
  for(const src of [doc.image,...doc.blocks.filter(b=>b.type==='image').map(b=>b.src)].filter(Boolean)){
   assert.ok((await stat(`public${src}`)).size>0,`${doc.slug}: missing image ${src}`);
  }
  await page.goto(`${origin}/source-archive/${doc.slug}/`);
  await expect(page.getByRole('heading',{level:1})).toHaveText(doc.title);
  const text=normalize(await page.locator('main article').innerText());
  for(const block of doc.blocks){
   if(block.text&&block.type!=='missing-image')assert.ok(text.includes(normalize(block.text)),`${doc.slug}: missing ${block.text.slice(0,90)}`);
   for(const item of block.items||[])assert.ok(text.includes(normalize(item)),`${doc.slug}: missing list item`);
   for(const row of block.rows||[])for(const cell of row)assert.ok(text.includes(normalize(cell)),`${doc.slug}: missing table cell`);
  }
  if(doc.kind==='post'){
   await page.goto(`${origin}/blog/${doc.slug}/`);
   await expect(page.getByRole('heading',{level:1})).toHaveText(doc.title);
   assert.ok(normalize(await page.locator('main article').innerText()).includes(normalize(doc.blocks.find(b=>b.type==='paragraph')?.text||'')),doc.slug);
  }
 }
 console.log(`PASS all ${report.pages} source pages and ${report.posts} full articles render their imported content`);
 for(const asset of imported.media.filter(m=>m.available)){
  assert.ok((await stat(`public${asset.src}`)).size>0,asset.src);
  assert.equal((await page.request.get(origin+asset.src)).status(),200,asset.src);
 }
 console.log(`PASS ${report.downloadedAssets} local media assets; ${report.failures.length} source 404s recorded`);
 await page.goto(`${origin}/join/`);
 for(const section of imported.config.membershipSections){
  for(const field of section.fields)assert.ok(await page.locator(`[name="${field.name}"]`).count()>0,field.label);
 }
 await expect(page.getByRole('link',{name:'Apply using YCP’s current form'})).toHaveAttribute('href',imported.config.membershipUrl);
 console.log(`PASS all ${report.membershipFields} membership fields and current application link`);
 await page.goto(`${origin}/faq/`);
 for(const faq of imported.config.faqs)await expect(page.getByRole('button',{name:faq.q,exact:true})).toBeVisible();
 await page.goto(`${origin}/contact/`);
 await expect(page.getByRole('link',{name:imported.config.email,exact:true})).toHaveAttribute('href',`mailto:${imported.config.email}`);
 for(const social of imported.config.socials)await expect(page.locator(`main a[href="${social.href}"]`)).toBeVisible();
 console.log('PASS original FAQs, published email and social links');
 await page.goto(`${origin}/media/`);
 await expect(page.locator('.migrated-media-grid figure')).toHaveCount(24);
 await page.getByRole('button',{name:'Show more assets'}).click();
 await expect(page.locator('.migrated-media-grid figure')).toHaveCount(48);
 await page.getByLabel('Search media library',{exact:true}).fill('no-such-media-asset-123');
 await expect(page.getByText('No media match this search.')).toBeVisible();
 await page.goto(`${origin}/blog/category/climate-change/`);
 await expect(page.locator('.article-card')).toHaveCount(imported.documents.filter(d=>d.kind==='post'&&d.categories.includes('Climate Change')).length);
 await page.goto(origin);
 await expect(page.locator('.nav').getByRole('link',{name:'International conferences',exact:true,includeHidden:true})).toHaveCount(0);
 await expect(page.locator('.nav').getByRole('link',{name:'International events',exact:true,includeHidden:true})).toHaveCount(1);
 console.log('PASS media search/pagination, category archive and retained navigation fix');
 await page.setViewportSize({width:390,height:844});
 for(const route of ['/about/','/leadership/president/','/blog/','/join/','/contact/','/media/','/source-archive/','/team/',...imported.documents.filter(d=>d.kind==='post').map(d=>`/blog/${d.slug}/`)]){
  await page.goto(origin+route);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),`Mobile overflow: ${route}`);
 }
 await page.goto(`${origin}/leadership/president/`);
 await page.screenshot({path:'.qa/president-migrated-mobile.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('PASS imported pages/articles fit mobile without runtime errors');
}finally{await browser.close()}
