<script setup  lang="ts">
import { useRouter } from "vue-router";
//const router = window.$router;
import { setLoggedIn } from "./AuthStore";
const router = useRouter()
setLoggedIn(false, "")
router.push("/");

</script>
<template>
  Hi
</template>
