<script setup  lang="ts">
/*
A dead simple component that logs the user out.
*/
import { useRouter } from "vue-router";
//const router = window.$router;
import { setLoggedIn } from "./AuthStore";
const router = useRouter()
async function logout() {
  // Tell the server to log us out
  await fetch('/logout', {
    credentials: 'include',
  })

  // Update login state in the store
  setLoggedIn(false, "")

  // Navigate to home
  router.push("/");
}
logout()
</script>
<template></template>
