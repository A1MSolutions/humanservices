<script setup>
defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});
</script>

<template>
    <div class="subj-landing__container">
        <h1>Find Policy Related to a Subject</h1>

        <p>Select a subject to look up executive orders, subregulatory guidance, court cases, rules, and more.</p>

    </div>
</template>

<style></style>
