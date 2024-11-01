<template v-if="timers && timers.length">
  <div @click.stop>

    <v-divider class="mb-2"></v-divider>
    <div
      v-for="(timer, i) in timers"
      :key="i"
      class="d-flex align-center my-2 justify-center">
      <v-icon :color=" timer.timerEnded  ? 'success' : ''" :class=" timer.timerEnded  ? 'shake' : ''">mdi-timer</v-icon>
      <v-btn
        icon
        :disabled=" timer.timerValue  <= 30"
        depressed
        @click="timer.timerValue -= 30">
        <v-icon>mdi-minus</v-icon>
      </v-btn>
      {{ timer.simpleDisplayValue }}
      <v-btn
        icon
        depressed
        @click="timer.timerValue += 30"><v-icon>mdi-plus</v-icon></v-btn>
      <v-btn
        v-if="! timer.timerRunning && ! timer.timerPaused  && !timer.timerEnded"
        rounded
        depressed
        @click=" timer.startTimer"> {{$t("recipe.timer.start")}} </v-btn>
      <template v-else>
        <v-btn
          v-if="(!timer.timerEnded && timer.timerRunning && !timer.timerPaused)"
          rounded
          depressed
          @click="timer.pauseTimer">
          {{$t("recipe.timer.pause")}}
        </v-btn>
        <span v-else-if="!timer.timerEnded " >
          <v-btn
            rounded
            depressed
            @click=" timer.resumeTimer">
            {{$t("recipe.timer.continue")}}
          </v-btn>
          <v-btn
            icon
            @click=" timer.resetTimer"><v-icon>mdi-restore</v-icon></v-btn>
        </span>
        <span v-else>
          <v-btn
            icon
            @click=" timer.resetTimer"><v-icon>mdi-restore</v-icon></v-btn>
        </span>
      </template>

    </div>
  </div>
</template>
<script lang="ts">
  import { computed } from "vue";
  import { useContext } from "@nuxtjs/composition-api";
  import { TranslateResult } from "vue-i18n"
  import useTimer from "~/composables/use-timer";
  // @ts-ignore typescript can't find our audio file, but it's there!

  export default {
    props: {
      text: {
        type: String,
        default: "",
      },
    },
    setup(props) {
      const { i18n } = useContext();
      // Makes regex work with multiple languages via locales
      const minuetStrings = computed<TranslateResult[]>(() => {
        console.log(i18n.availableLocales);
        const result: TranslateResult[] = [];
        i18n.availableLocales.forEach((locale) => {
          result.push(i18n.t("recipe.timer.minute", locale ))
          result.push(i18n.t("recipe.timer.minutes", locale ))
        })
        return result
      })

      const extractTimersFromText = (text: string) => {
        const regexMins = new RegExp(`\\b(\\d+)\\s*(${minuetStrings.value.join("|")})\\b`, "gi");
        const matchesMin = text.matchAll(regexMins);
        const timers = [];
        for (const match of matchesMin) {
          const timer = useTimer("00",match[1], "00", { padTimes: false })
          timer.initializeTimer();
          timers.push(timer);
        }
        return timers;
      };

      return {
        timers:  extractTimersFromText(props.text as string)
      }
    },
  };
</script>
<style scoped>
  .shake {
    animation: shake 0.82s cubic-bezier(0.36, 0.07, 0.19, 0.97) infinite;
  }
  @keyframes shake {
    10%, 90% {
      transform: translate3d(-1px, 0, 0);
    }
    20%, 80% {
      transform: translate3d(2px, 0, 0);
    }
    30%, 50%, 70% {
      transform: translate3d(-4px, 0, 0);
    }
    40%, 60% {
      transform: translate3d(4px, 0, 0);
    }
  }
</style>
