<script setup lang="ts">
/*
Handles signup and login for the application
*/

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

// The value of the text fields on the signup tab
const signupUsername = ref(undefined);
const signupPassword = ref(undefined);

// The value of the text fields on the login tab
const loginUsername = ref(undefined);
const loginPassword = ref(undefined);

// Redirect to project if logged in already
if (isLoggedIn()) {
  router.push('/');
}


async function signUp() {
  /*
    Handle signup request with the server
  */

  // Don't allow if no values
  if (signupUsername.value == undefined || signupPassword.value == undefined) {
    return;
  }

  // Attempt to sign up
  const response = await fetch('/signup', {
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

  // Parse response 
  const responseJson = await response.json()

  // Did we sign up?
  if (response.status == 200 && responseJson["success"] == true) {
    // Yes, go to messenger
    setLoggedIn(true, signupUsername.value);
    router.push('/');
  } else {
    // No, something went wrong
    alert("Unable to sign up. " + responseJson["message"])
  }
}
async function login() {
  // Don't allow if no values
  if (loginUsername.value == undefined || loginPassword == undefined) {
    return;
  }

  // Attempt to login
  const response = await fetch('/signin', {
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
  const responseJson = await response.json()
  // Did we login?
  if (response.status == 200 && responseJson["success"] == true) {
    // Yes, go to messenger
    setLoggedIn(true, loginUsername.value);
    router.push('/');
  } else { alert("Unable to log in. " + responseJson["message"]) }
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
              <CardDescription>Sign up for instant messaging</CardDescription>
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
              <CardDescription>Login to instant messaging</CardDescription>
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
