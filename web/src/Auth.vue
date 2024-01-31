<script setup lang="ts">
import { ref } from 'vue';
import router from './router';
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { setLoggedIn, isLoggedIn } from '@/AuthStore';
const signupUsername = ref(undefined);
const signupPassword = ref(undefined);
const loginUsername = ref(undefined);
const loginPassword = ref(undefined);

if (isLoggedIn()) {
  router.push('/');
}

async function signUp() {
  if (signupUsername.value == undefined || signupPassword.value == undefined) {
    return;
  }
  const response = await fetch('http://127.0.0.1:5000/signup', {
    method: "POST",
    credentials: 'include',
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "username": signupUsername.value,
      "password": signupPassword.value
    })
  })
  if ((await response.json())["success"] == true) {
    setLoggedIn(true, signupUsername.value);
    router.push('/');
  }
}
async function login() {
  if (loginUsername.value == undefined || loginPassword == undefined) {
    return;
  }
  const response = await fetch('http://127.0.0.1:5000/signin', {
    method: "POST",
    credentials: 'include',
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "username": loginUsername.value,
      "password": loginPassword.value
    })
  })
  if ((await response.json())["success"] == true) {
    setLoggedIn(true, loginUsername.value);
    router.push('/');
  }
}
</script>

<template>
  <div class="flex justify-center items-center h-screen">

    <Tabs default-value="signup" class="w-[400px]">
      <TabsList class="grid w-full grid-cols-2">
        <TabsTrigger value="signup"> Sign Up </TabsTrigger>
        <TabsTrigger value="login"> Log In </TabsTrigger>
      </TabsList>
      <TabsContent value="signup">
        <Card>
          <form @submit.prevent="signUp">
            <CardHeader>
              <CardTitle>Sign Up</CardTitle>
              <CardDescription>Sign up for thingy</CardDescription>
            </CardHeader>
            <CardContent class="space-y-2">
              <div class="space-y-1">
                <Label for="username">Username</Label>
                <Input v-model="signupUsername" id="username" />
              </div>
              <div class="space-y-1">
                <Label for="password">Password</Label>
                <Input v-model="signupPassword" id="password" type="password" />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit">Create Account</Button>
            </CardFooter>
          </form>
        </Card>
      </TabsContent>
      <TabsContent value="login">
        <Card>
          <form @submit.prevent="login">
            <CardHeader>
              <CardTitle>Log In</CardTitle>
              <CardDescription>Log in to thingy</CardDescription>
            </CardHeader>
            <CardContent class="space-y-2">
              <div class="space-y-1">
                <Label for="username">Username</Label>
                <Input v-model="loginUsername" id="username" />
              </div>
              <div class="space-y-1">
                <Label for="password">Password</Label>
                <Input v-model="loginPassword" id="password" type="password" />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit">Log In</Button>
            </CardFooter>
          </form>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>
