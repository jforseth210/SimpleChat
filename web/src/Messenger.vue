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
let selectedConversationID = ref(0);
let messageInput = ref("");
let newConversationPersonInput = ref("");
const currentUser = getUsername();

function selectConversation(conversation: any) {
  /*
  Sets selectedConversations and reloads the messages
  */
  selectedConversationID.value = conversation.id;
  loadConversations();
}

async function sendMessage() {
  // Send the message to the server
  const response = await fetch("/send-message", {
    credentials: "include",
    method: "POST",
    body: JSON.stringify({
      "conversationId": selectedConversationID.value,
      "message": messageInput.value
    })
  })
  if (response.status === 200) {
    // Message sent
    // Reload the conversations
    loadConversations();

    // Clear the input
    messageInput.value = "";
  }
}
async function loadConversations() {
  /*
  * Fetches all messages from the server
  */
  const response = await fetch("/conversations", { credentials: "include" })

  // We're not logged in. We should redirect to login
  if (response.status === 401) {
    setLoggedIn(false, "");
    router.push("/login");
  }
  // Parse the JSON
  const responseJson = await response.json();

  // Handle no conversations
  if (responseJson.keys().length == 0) {
    conversations.value = [];
  } else {
    conversations.value = responseJson;
  }

  // Is selectedConversationId a valid conversation?
  if (conversations.value.filter((conversation: any) => { conversation.id == selectedConversationID.value }).length == 0) {
    // Nope, set to the id of the first conversation
    selectedConversationID.value = conversations.value[0].id
  }
}

// Initially load the messages
loadConversations();

// I *really* wanted to play with websockets to handle
// message delivery, but I don't have time, so we'll
// poll the server instead
setInterval(() => { loadConversations() }, 1000);

async function addConversation() {
  /*
  Handle conversation creation
  */
  const response = await fetch("/add-conversation", {
    credentials: "include",
    method: "POST",
    body: JSON.stringify({
      "user": newConversationPersonInput.value
    })
  });

  if (response.status === 200) {
    // Conversation created! Reload conversations
    loadConversations();
  } else if (response.status == 404) {
    // Handle no user
    alert("User doesn't exist")
  } else if (response.status == 400) {
    // Handle conversation already exists
    alert("Conversation already exists")
  }
}
</script>

<template>
  <div class="flex">
    <div class="w-1/4 h-screen">
      <!-- Conversation list -->
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
                    <p>Enter the username of the person you want to start a conversation with</p>
                    <Input v-model="newConversationPersonInput" />
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
              :class="{ 'bg-gray-300': selectedConversationID === conversation.id }" tabindex="0"
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
            v-if="conversations.length > 0 && conversations.filter((conversation: any) => conversation.id == selectedConversationID)[0].messages.length > 0"
            v-for="message in conversations.filter((conversation: any) => conversation.id ==
              selectedConversationID)[0].messages" :key="message.text" class="rounded-lg m-2 p-2 w-fit" :class="{
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
