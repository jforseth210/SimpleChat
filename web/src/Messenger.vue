<script setup lang="ts">
import { ref } from "vue";
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useRouter } from "vue-router";
import { setLoggedIn, getUsername } from "./AuthStore";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
const router = useRouter();
let conversations: any = ref([]);
let selectedConversation = ref(0);
let messageInput = ref("");
const currentUser = getUsername();

function selectConversation(message: any) {
  console.log("Selecting conversation: " + message)
  selectedConversation.value = message.id;
  //loadConversation(selectedConversation.value);
  loadConversations();
}
/*
async function loadConversation(conversationId: number) {
  console.log("Loading conversation: " + conversationId)
  const response = await fetch("http://127.0.0.1:5000/conversation", {
    credentials: "include", method: "POST", body: JSON.stringify({ "id": conversationId })
  })
  const responseJson = await response.json()
  conversations.value = conversations.value.map((conversation: any) => {
    if (conversation.id == selectedConversation.value) {
      conversation.messages = responseJson;
    }
    return conversation
  })
}
*/

async function sendMessage() {
  console.log("Sending message: " + messageInput.value)
  const response = await fetch("http://127.0.0.1:5000/send-message", { credentials: "include", method: "POST", body: JSON.stringify({ "conversationId": selectedConversation.value, "message": messageInput.value }) })
  if (response.status === 200) {
    //loadConversation(selectedConversation.value);
    loadConversations();
    messageInput.value = "";
  }
}
async function loadConversations() {
  console.log("Loading conversations")
  const response = await fetch("http://127.0.0.1:5000/conversations", { credentials: "include" })
  if (response.status === 401) {
    setLoggedIn(false, "");
    router.push("/login");
  }
  const responseJson = await response.json();
  if (responseJson.keys().length == 0) {
    conversations.value = [];
  } else {
    conversations.value = responseJson;
  }
  if (conversations.value.filter((conversation: any) => { conversation.id == selectedConversation.value }).length == 0) {
    selectedConversation.value = conversations.value[0].id
  }
  console.log(conversations.value)
  // conversations.value = [];
}
setInterval(() => { loadConversations() }, 1000);
loadConversations();
const newConversationSelectedPerson = ref("");
async function addConversation() {
  const response = await fetch("http://127.0.0.1:5000/add-conversation", {
    credentials: "include",
    method: "POST",
    body: JSON.stringify({
      "user": newConversationSelectedPerson.value
    })
  });
  if (response.status === 200) {
    loadConversations();
  } else if (response.status == 404) {
    alert("User doesn't exist")
  } else if (response.status == 400) {
    alert("Conversation already exists")
  }
}
</script>

<template>
  <div class="flex">
    <div class="w-1/4 h-screen">
      <ScrollArea class="h-full w-full">
        <div class="p-4">
          <div class="flex mb-2 flex-row items-center justify-between">
            <h1 class="text-2xl font-bold leading-none">
              Conversations
            </h1>

            <AlertDialog>
              <AlertDialogTrigger>
                <Button click="addConversation">+</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Add A Conversation</AlertDialogTitle>
                  <AlertDialogDescription>
                    <p> Select someone to start a conversation</p>
                    <Input v-model="newConversationSelectedPerson" />
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction @click="addConversation">Add</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
          <div v-for="conversation in conversations" :key="conversation.id">
            <div @click="selectConversation(conversation)" class="p-2 rounded-lg cursor-pointer hover:bg-gray-300"
              :class="{ 'bg-gray-300': selectedConversation === conversation.id }" tabindex="0"
              @keypress.enter="selectConversation(conversation)">
              <div class="flex flex-row">
                <Avatar class="w-12 h-12">
                  <AvatarFallback>{{ conversation.user ? conversation.user.split(" ").map((n: string) =>
                    n[0].toUpperCase()).join("") : ""
                  }}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h1 class="text-base ml-2">{{ conversation.user }}</h1>
                  <p v-if="conversation.messages && conversation.messages.length > 0" class="text-sm ml-2">{{
                    conversation.messages[conversation.messages.length - 1].text.substring(0, 50)
                    + "..." }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
    <div class="grow flex flex-col h-screen">
      <div class="w-full text-right p-4">
        <RouterLink to="/logout" class="text-blue-600 dark:text-blue-500 hover:underline">Logout</RouterLink>
      </div>
      <div class="grow overflow-auto">
        <div class="flex flex-col">
          <div
            v-if="conversations.length > 0 && conversations.filter((conversation: any) => conversation.id == selectedConversation)[0].messages.length > 0"
            v-for="message in conversations.filter((conversation: any) => conversation.id ==
              selectedConversation)[0].messages" :key="message.text" class="rounded-lg m-2 p-2 w-fit" :class="{
    'bg-gray-300 text-left self-start': message.from !== currentUser,
    'bg-blue-600 text-right text-white self-end': message.from === currentUser
  }">{{ message.text }}
          </div>
        </div>
      </div>
      <form @submit.prevent="sendMessage">
        <div class="flex flex-row p-4">
          <Input v-model="messageInput" class=" w-full" placeholder="Type a message" />
          <Button>Send</Button>
        </div>
      </form>
    </div>
  </div>
</template>
