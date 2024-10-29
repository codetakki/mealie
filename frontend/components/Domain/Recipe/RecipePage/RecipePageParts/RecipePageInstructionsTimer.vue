<template v-if="timers && timers.length">
  <div @click.stop>

    <v-divider class="mb-2"></v-divider>
    <div
      v-for="(timer, i) in timers"
      :key="i"
      class="d-flex align-center my-2 justify-center">
      <v-icon :color="timer.done.value ? 'success' : ''" :class="timer.done.value ? 'shake' : ''">mdi-timer</v-icon>
      <v-btn
        icon
        :disabled="timer.remainingTime.value <= 30"
        depressed
        @click="timer.remainingTime.value -= 30"><v-icon>mdi-minus</v-icon></v-btn>
      {{ timer.hours.value ? timer.hours.value + "h" : "" }} {{ timer.minutes.value ? timer.minutes.value + "m" : "" }}
      {{ (timer.seconds.value || !timer.minutes.value) ? timer.seconds.value + "s" : "" }}
      <v-btn
        icon
        depressed
        @click="timer.remainingTime.value += 30"><v-icon>mdi-plus</v-icon></v-btn>
      <v-btn
        v-if="!timer.isCounting.value && !timer.hasStarted.value"
        rounded
        depressed
        @click="timer.startAlarm"> {{$t("recipe.timer.start")}} </v-btn>
      <v-btn
        v-else-if="(timer.hasStarted.value && timer.isCounting.value)"
        rounded
        depressed
        @click="timer.pauseTimer"> {{$t("recipe.timer.pause")}} </v-btn>
      </v-btn>
      <span v-else-if="!timer.done.value">
        <v-btn
          rounded
          depressed
          @click="timer.startAlarm">
          {{$t("recipe.timer.continue")}}
        </v-btn>
        <v-btn
          icon
          @click="timer.resetTimer"><v-icon>mdi-restore</v-icon></v-btn>
      </span>
      <span v-else>
        <v-btn
          icon
          @click="timer.resetTimer"><v-icon>mdi-restore</v-icon></v-btn>
      </span>
    </div>
  </div>
</template>
<script lang="ts">
  import { computed, ref, onBeforeUnmount } from "vue";
import { useContext } from "@nuxtjs/composition-api";

  import { TranslateResult } from "vue-i18n"
  // @ts-ignore typescript can't find our audio file, but it's there!
  import timerAlarmAudio from "~/assets/audio/kitchen_alarm.mp3";
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
      const minuetStrings = computed<string[]>(() => {
        console.log(i18n.availableLocales);
        const result: TranslateResult[] = [];
        i18n.availableLocales.forEach((locale) => {
          result.push(i18n.t("recipe.timer.minute", locale ))
          result.push(i18n.t("recipe.timer.minutes", locale ))
        })
        return result
      })

      const extractMinutes = (text: string) => {
        const regexMins = new RegExp(`\\b(\\d+)\\s*(${minuetStrings.value.join("|")})\\b`, "gi");
        const matchesMin = text.matchAll(regexMins);
        const timers = [];
        for (const match of matchesMin) {
          timers.push(createTimer(Number(match[1]) * 60));
        }
        return timers;
      };
      const timers = computed(() => {
        return extractMinutes(props.text as string);
      });

      const createTimer = (totalSeconds: number) => {
        const remainingTime = ref(totalSeconds);
        const hours = computed(() => Math.floor(remainingTime.value / 3600));
        const minutes = computed(() => Math.floor((remainingTime.value % 3600) / 60));
        const seconds = computed(() => remainingTime.value % 60);
        const isCounting = ref(false);
        const hasStarted = ref(false)
        const done = ref(false)

        let timer = null;

        const formattedTime = computed(() => {
          const hrs = Math.floor(remainingTime.value / 3600);
          const mins = Math.floor((remainingTime.value % 3600) / 60);
          const secs = remainingTime.value % 60;
          return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs
            .toString()
            .padStart(2, "0")}`;
        });

        const startAlarm = () => {
          if (remainingTime.value > 0) {
            isCounting.value = true;
            timer = setInterval(updateTimer, 1000);
            hasStarted.value = true
          }
        };

        // ts doesn't recognize timerAlarmAudio because it's a weird import
        // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
        const alarmSound = new Audio(timerAlarmAudio);
        alarmSound.loop = true;
        const updateTimer = () => {
          if (remainingTime.value >= 1) {
            remainingTime.value--;
          } else {
            pauseTimer();
            alarmSound.play();
            done.value = true;
          }
        };

        const pauseTimer = () => {
          isCounting.value = false;
          clearInterval(timer);
          alarmSound.pause();
        };

        const resetTimer = () => {
          clearInterval(timer);
          remainingTime.value = totalSeconds;
          isCounting.value = false;
          hasStarted.value = false;
          done.value = false;
          alarmSound.pause();
        };

        onBeforeUnmount(() => {
          resetTimer();
        });
        return {
          hours,
          minutes,
          seconds,
          remainingTime,
          isCounting,
          formattedTime,
          startAlarm,
          resetTimer,
          pauseTimer,
          originalTimer: totalSeconds,
          hasStarted,
          done
        };
      };

      return {
        timers,
      };
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
