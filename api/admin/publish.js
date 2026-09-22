import crypto from 'node:crypto';

function signature(value){return crypto.createHmac('sha256',process.env.ADMIN_SESSION_SECRET||process.env.ADMIN_PASSWORD||'').update(value).digest('base64url');}
function isAdmin(req){const raw=(req.headers.cookie||'').match(/dardic_admin=([^;]+)/)?.[1];if(!raw)return false;const [value,sig]=raw.split('.');return !!value&&sig===signature(value);}
function slug(v){return v.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim().replace(/[^\p{L}\p{N}]+/gu,'-').replace(/^-+|-+$/g,'').slice(0,90)||'article';}
function q(v){return JSON.stringify(v);}
function md(b){const tags=String(b.tags||'').split(',').map(x=>x.trim()).filter(Boolean);const langs=String(b.relatedLanguages||'').split(',').map(x=>x.trim()).filter(Boolean);return ['---','title: '+q(String(b.title).trim()),'description: '+q(String(b.description||'').trim()),'pubDate: '+String(b.pubDate||new Date().toISOString().slice(0,10)),'lang: '+String(b.lang||'en'),'category: '+q(String(b.category||'Documentation')),tags.length?'tags: ['+tags.map(q).join(', ')+']':'tags: []',langs.length?'relatedLanguages: ['+langs.map(q).join(', ')+']':'relatedLanguages: []',b.authorName?'authorName: '+q(String(b.authorName).trim()):'',b.authorRole?'authorRole: '+q(String(b.authorRole).trim()):'',b.publication?'publication: '+q(String(b.publication).trim()):'',b.edition?'edition: '+q(String(b.edition).trim()):'',b.issueNumber?'issueNumber: '+Number(b.issueNumber):'','status: '+(b.status==='draft'?'draft':'published'),'---','','# '+String(b.title).trim(),' ',String(b.content||'').trim(),''].filter(Boolean).join('\n');}
export default async function handler(req,res){
 if(req.method!=='POST')return res.status(405).json({ok:false,error:'Method not allowed.'});
 if(!isAdmin(req))return res.status(401).json({ok:false,error:'Admin login required.'});
 const b=req.body||{};if(!String(b.title||'').trim()||!String(b.content||'').trim())return res.status(400).json({ok:false,error:'Title and article body are required.'});
 if(!process.env.GITHUB_TOKEN)return res.status(500).json({ok:false,error:'GITHUB_TOKEN is not configured on Vercel.'});
 const repo=process.env.GITHUB_REPO||'xl8saif/dardic-archive',branch=process.env.GITHUB_BRANCH||'main',path='src/content/articles/'+slug(String(b.title))+'.md';
 const r=await fetch('https://api.github.com/repos/'+repo+'/contents/'+path,{method:'PUT',headers:{Authorization:'Bearer '+process.env.GITHUB_TOKEN,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'},body:JSON.stringify({message:'Publish article: '+String(b.title),content:Buffer.from(md(b),'utf8').toString('base64'),branch})});
 const out=await r.json();if(!r.ok)return res.status(r.status).json({ok:false,error:out.message||'GitHub publication failed.'});
 return res.status(200).json({ok:true,path});
}