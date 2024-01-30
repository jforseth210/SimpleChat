<script setup lang="ts">
import { ref } from 'vue';
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
const signupUsername = ref(undefined);
const signupPassword = ref(undefined);
const signinUsername = ref(undefined);
const signinPassword = ref(undefined);

async function signUp() {
  const response = await fetch('http://127.0.0.1:8000/api/signup', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "username": signupUsername.value,
      "password": signupPassword.value
    })
  })
  console.log(await (response.json()));
}
async function signIn() {

  if (signinUsername.value === undefined) return
  if (signinPassword.value === undefined) return
  let formData = new FormData();
  formData.append('username', signinUsername.value);
  formData.append('password', signinPassword.value);
  const response = await fetch('http://127.0.0.1:8000/token', {
    method: "POST",
    body: formData
  })
  console.log(await (response.json()));
}
</script>

<template>
  <div class="flex justify-center items-center h-screen">

    <Tabs default-value="signup" class="w-[400px]">
      <TabsList class="grid w-full grid-cols-2">
        <TabsTrigger value="signup"> Sign Up </TabsTrigger>
        <TabsTrigger value="signin"> Sign In </TabsTrigger>
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
      <TabsContent value="signin">
        <Card>
          <form @submit.prevent="signIn">
            <CardHeader>
              <CardTitle>Sign In</CardTitle>
              <CardDescription>Sign in to thingy</CardDescription>
            </CardHeader>
            <CardContent class="space-y-2">
              <div class="space-y-1">
                <Label for="username">Username</Label>
                <Input v-model="signinUsername" id="username" />
              </div>
              <div class="space-y-1">
                <Label for="password">Password</Label>
                <Input v-model="signinPassword" id="password" type="password" />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit">Sign In</Button>
            </CardFooter>
          </form>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>
