<script setup>
import { computed, provide } from "vue";

import TocTitle from "sharedComponents/TOC/TocTitle.vue";
import TocSubchapter from "sharedComponents/TOC/TocSubchapter.vue";
import TocPart from "sharedComponents/TOC/TocPart.vue";

const props = defineProps({
    structure: {
        type: Object,
        required: true,
    },
});

const titleIdentifier = computed(() => props.structure.identifier[0]);

provide("titleIdentifier", titleIdentifier.value);

const titleLabel = computed(() =>
    `${props.structure.label_level} - ${props.structure.label_description}`.replace(
        /&amp;/g,
        "&"
    )
);

const directChild = computed(() => {
    const directChapter = props.structure.children.find(
        (child) => child.type === "chapter"
    );
    if (directChapter) return directChapter;

    const subtitle = props.structure.children.find(
        (child) => child.type === "subtitle"
    );
    if (subtitle && Array.isArray(subtitle.children)) {
        const chapterUnderSubtitle = subtitle.children.find(
            (child) => child.type === "chapter"
        );
        if (chapterUnderSubtitle) return chapterUnderSubtitle;
        return subtitle;
    }
    return undefined;
});

const subtitleChild = computed(() =>
    props.structure.children.find((child) => child.type === "subtitle")
);

const subtitleCount = computed(
    () => (props.structure.children || []).filter((c) => c?.type === "subtitle").length
);

const titleSubheading = computed(() => {
    const chapter = directChild.value;
    const subtitle = subtitleChild.value;

    const chapterStr = chapter && chapter.type === "chapter"
        ? `${chapter.label_level} - ${chapter.label_description}`
        : undefined;
    const subtitleStr = subtitle
        ? `${subtitle.label_level} - ${subtitle.label_description}`
        : undefined;

    const includeSubtitle = subtitleCount.value === 1;
    const includeChapter = subtitleCount.value === 0;
    const combined = [includeSubtitle ? subtitleStr : undefined, includeChapter ? chapterStr : undefined]
        .filter(Boolean)
        .join(" | ");
    return combined ? combined.replace(/&amp;/g, "&") : undefined;
});

// Build sections grouped by subtitle. Each section contains an ordered list of entries
// that can be either subchapters or chapters (with their own parts and subchapters).
// If there are no subtitles, fall back to grouping by top-level chapters under the title.
const subtitleSections = computed(() => {
    const sections = [];
    const children = Array.isArray(props.structure.children)
        ? props.structure.children
        : [];

    const subtitles = children.filter((c) => c?.type === "subtitle");

    if (subtitles.length > 0) {
        for (const subtitle of subtitles) {
            const entries = [];
            const children = subtitle.children ?? [];
            const chapterNodes = children.filter((n) => n?.type === "chapter");
            const subchapterNodes = children.filter((n) => n?.type === "subchapter");

            if (chapterNodes.length > 0) {
                const seen = new Set();
                for (const node of chapterNodes) {
                    const chapterId = Array.isArray(node.identifier)
                        ? node.identifier.join(".")
                        : String(node.identifier ?? "");
                    if (seen.has(chapterId)) continue;
                    seen.add(chapterId);

                    const chapterSubchapters = [];
                    const chapterParts = [];
                    for (const chChild of node.children ?? []) {
                        if (chChild?.type === "subchapter") chapterSubchapters.push(chChild);
                        if (chChild?.type === "part") chapterParts.push(chChild);
                    }
                    entries.push({
                        kind: "chapter",
                        chapter: node,
                        subchapters: chapterSubchapters,
                        parts: chapterParts,
                    });
                }
            } else {
                for (const node of subchapterNodes) {
                    entries.push({ kind: "subchapter", subchapter: node });
                }
            }

            sections.push({ subtitle, entries });
        }
        return sections;
    }

    // Fallback: no subtitles present. Group by top-level chapters under the title.
    const topLevelChapters = children.filter((c) => c?.type === "chapter");
    if (topLevelChapters.length > 0) {
        const entries = [];
        for (const chapter of topLevelChapters) {
            const chapterSubchapters = [];
            const chapterParts = [];
            for (const chChild of chapter.children ?? []) {
                if (chChild?.type === "subchapter") chapterSubchapters.push(chChild);
                if (chChild?.type === "part") chapterParts.push(chChild);
            }
            entries.push({
                kind: "chapter",
                chapter,
                subchapters: chapterSubchapters,
                parts: chapterParts,
            });
        }
        sections.push({ subtitle: undefined, entries });
    }

    return sections;
});
</script>

<template>
    <div class="toc__container--inner">
        <TocTitle :title="titleLabel" :subheading="titleSubheading" />
        <div v-for="(section, idx) in subtitleSections" :key="section.subtitle?.label_level || idx">
            <h3 v-if="section.subtitle && subtitleCount > 1" class="toc-subtitle__heading">
                {{ section.subtitle.label_level }} - {{ section.subtitle.label_description }}
            </h3>
            <template v-for="(entry, eidx) in section.entries" :key="eidx">
                <template v-if="entry.kind === 'subchapter'">
                    <TocSubchapter :subchapter="entry.subchapter" />
                </template>
                <template v-else-if="entry.kind === 'chapter'">
                    <div class="toc-subchapter__container">
                        <h4 class="toc-subchapter__label">
                            {{ entry.chapter.label_level }} - {{ entry.chapter.label_description }}
                        </h4>
                        <TocSubchapter
                            v-for="subchapter in entry.subchapters"
                            :key="subchapter.label_level"
                            :subchapter="subchapter"
                        />
                        <TocPart
                            v-for="part in entry.parts"
                            :key="part.label_level"
                            :part="part"
                        />
                    </div>
                </template>
            </template>
        </div>
    </div>
</template>
