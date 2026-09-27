from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Mapping
from app.services.canonical_draft_gate import CanonicalDraft

CANONICAL_LANGUAGES=("bg","en","ru","ro")
@dataclass(frozen=True)
class LanguageContent:
    name:str
    short:str
    long:str
    meta_title:str
    meta_description:str
@dataclass(frozen=True)
class ContentReadiness:
    draft:CanonicalDraft
    content:Mapping[str,LanguageContent]
    blockers:tuple[str,...]
    ready:bool
    write_performed:bool=False

def evaluate_content_readiness(draft:CanonicalDraft, content:Mapping[str,LanguageContent],
                               required_languages:tuple[str,...]=CANONICAL_LANGUAGES)->ContentReadiness:
    blockers=[]
    unknown=sorted(set(content)-set(CANONICAL_LANGUAGES))
    if unknown: blockers.append("UNKNOWN_LANGUAGE:"+",".join(unknown))
    for lang in required_languages:
        c=content.get(lang)
        if c is None:
            blockers.append("MISSING_LANGUAGE:"+lang);continue
        for field in ("name","short","long","meta_title","meta_description"):
            if not str(getattr(c,field,"") or "").strip(): blockers.append("MISSING_CONTENT:"+lang+":"+field)
    return ContentReadiness(draft,dict(content),tuple(blockers),not blockers,False)
