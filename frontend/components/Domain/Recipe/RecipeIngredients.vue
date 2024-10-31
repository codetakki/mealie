<template>
  <div v-if="value && value.length > 0">
    <div class="d-flex justify-start">
      <h2 class="mb-2 mt-1">{{ $t("recipe.ingredients") }}</h2>
      <AppButtonCopy
btn-class="ml-auto"
        :copy-text="ingredientCopyText" />
    </div>
    <div>
      <div
        v-for="(step, stepIndex) in compInstructions"
        :key="'step' + stepIndex">
        <div v-if="!hideStepHeaders" class="text-subtitle-1">{{ step.title || step.summary || $t("recipe.step-index", { step: stepIndex + 1 }) }}</div>
        <div
          v-for="(ingredient, index) in mappedIngredients[step.id || '']"
          :key="'ingredient' + index">
            <h3
              v-if="showTitleEditor[ingredient.referenceId || '']"
              class="mt-2">{{ ingredient.title }}
            </h3>
            <v-divider v-if="showTitleEditor[ingredient.referenceId || '']"></v-divider>
            <v-list-item
              dense
              @click="toggleChecked(ingredient.referenceId || '')">
              <v-checkbox
                hide-details
                :value="checked[ingredient.referenceId ||'']"
                class="pt-0 my-auto py-auto"
                color="secondary" />
              <v-list-item-content :key="ingredient.quantity">
                <RecipeIngredientListItem
                  :ingredient="ingredient"
                  :disable-amount="disableAmount"
                  :scale="scale" />
              </v-list-item-content>
            </v-list-item>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
  import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
  import { parseIngredientText } from "~/composables/recipes";
  import { RecipeIngredient, RecipeStep } from "~/lib/api/types/recipe";

  export default defineComponent({
    components: { RecipeIngredientListItem },
    props: {
      value: {
        type: Array as () => RecipeIngredient[],
        default: () => [],
      },
      disableAmount: {
        type: Boolean,
        default: false,
      },
      scale: {
        type: Number,
        default: 1,
      },
      instructions: {
        type: Array as () => RecipeStep[],
        default: () => [],
      },
      isCookMode: {
        type: Boolean,
        default: false,
      }
    },
    setup(props) {
      function validateTitle(title?: string) {
        return !(title === undefined || title === "" || title === null);
      }

      const state = reactive({
        // Us ids instead of index to make it more robust incase of multiple ingredients in different steps
        checked: Object.fromEntries(props.value.map(item => [item.referenceId, false])),
        showTitleEditor: computed(() => Object.fromEntries(props.value.map((x) => [x.referenceId || "", validateTitle(x.title)]))),

      });

      const ingredientCopyText = computed(() => {
        const components: string[] = [];
        props.value.forEach((ingredient) => {
          if (ingredient.title) {
            if (components.length) {
              components.push("");
            }

            components.push(`[${ingredient.title}]`);
          }

          components.push(parseIngredientText(ingredient, props.disableAmount, props.scale, false));
        });

        return components.join("\n");
      });

      function toggleChecked(index: string) {
        state.checked[index] = !state.checked[index];
      }
      function partOfStep(step: RecipeStep, ingredientId: string): boolean | undefined {
        return step.ingredientReferences?.includes(ingredientId)
      }
      const { i18n } = useContext();

      // filter out instructions without ingredients, add "other ingredients"
      const compInstructions = computed(() => {
        if (!props.instructions ) {
          return [];
        }
        const result = props.instructions.filter((step) => step.ingredientReferences && step.ingredientReferences.length > 0)
        result.push({
          title: i18n.t("recipe.other-ingredients") as string,
          text: "",
          id: "none",
          ingredientReferences: []
        });
        return result
      })
      // Map to recipe steps
      const mappedIngredients = computed(() => {
        const steps : Record<string, string[]> = Object.fromEntries(props.instructions.map(item => [item.id, item.ingredientReferences?.map(x => x.referenceId) || []]));
        const result: Record<string, RecipeIngredient[]> = {}
        const stepsAdded : RecipeIngredient["referenceId"][] = []
        Object.keys(steps).forEach((key) => {
          if(key !== "none") {
            result[key] = props.value.filter(x => {
              if(steps[key].includes(x.referenceId || "")){
                stepsAdded.push(x.referenceId)
                return true
              }
              return false
            })
          }
        })
        result.none = props.value.filter(x => !stepsAdded.includes(x.referenceId || ""))
        return result
      })
      const hideStepHeaders = computed(() => {
        if (props.isCookMode){
          return false
        }
        return !props.isCookMode || !props.instructions.some((step) => step.ingredientReferences && step.ingredientReferences.length > 0)
      })
      return {
        ...toRefs(state),
        ingredientCopyText,
        toggleChecked,
        partOfStep,
        compInstructions,
        mappedIngredients,
        hideStepHeaders
      };
    },
  });
</script>

<style>
.dense-markdown p {
  margin: auto !important;
}
</style>
