<script setup>
import { computed, provide } from "vue";

import TocTitle from "sharedComponents/TOC/TocTitle.vue";
import TocSubchapter from "sharedComponents/TOC/TocSubchapter.vue";

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

const titleSubheading = computed(() => {
    const chapter = directChild.value;
    const subtitle = subtitleChild.value;

    const chapterStr = chapter && chapter.type === "chapter"
        ? `${chapter.label_level} - ${chapter.label_description}`
        : undefined;
    const subtitleStr = subtitle
        ? `${subtitle.label_level} - ${subtitle.label_description}`
        : undefined;

    const combined = [subtitleStr, chapterStr].filter(Boolean).join(" | ");
    return combined ? combined.replace(/&amp;/g, "&") : undefined;
});
</script>

<template>
    <div class="toc__container--inner">
        <TocTitle :title="titleLabel" :subheading="titleSubheading" />
        <TocSubchapter
            v-for="subchapter in directChild.children"
            :key="subchapter.label_lebel"
            :subchapter="subchapter"
        />
    </div>
</template>
