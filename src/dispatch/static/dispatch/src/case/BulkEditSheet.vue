<template>
  <v-bottom-sheet
    v-model="showBulkEdit"
    :scrim="false"
    persistent
    no-click-animation
    :retain-focus="false"
  >
    <handoff-dialog />
    <closed-dialog />
    <v-card :loading="bulkEditLoading" rounded="0">
      <v-list>
        <v-list-item>
          <v-list-item-subtitle>{{ selected.length }} selected</v-list-item-subtitle>

          <template #append>
            <v-btn variant="text" @click="showHandoffDialog()">
              <v-icon>mdi-account-arrow-right</v-icon>
              Handoff
            </v-btn>

            <v-btn variant="text" @click="saveBulk({ status: 'New' })">
              <v-icon>mdi-alert-decagram</v-icon>
              Mark New
            </v-btn>

            <v-btn variant="text" @click="saveBulk({ status: 'Triage' })">
              <v-icon>mdi-check</v-icon>
              Mark Triage
            </v-btn>

            <v-btn variant="text" @click="showClosedDialog()">
              <v-icon>mdi-close</v-icon>
              Mark Closed
            </v-btn>

            <v-btn variant="text" color="primary" @click="deleteBulk()">
              <v-icon color="primary">mdi-delete</v-icon>
              Delete
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </v-bottom-sheet>
</template>

<script setup>
import { computed, ref, watchEffect } from "vue"
import { useStore } from "vuex"
import HandoffDialog from "@/case/HandoffDialog.vue"
import ClosedDialog from "@/case/ClosedDialog.vue"

const store = useStore()

const selected = computed(() => store.state.case_management.table.rows.selected)
const bulkEditLoading = computed(() => store.state.case_management.table.bulkEditLoading)
const showBulkEdit = ref(false)

watchEffect(() => {
  showBulkEdit.value = selected.value.length > 0
})

const saveBulk = (status) => store.dispatch("case_management/saveBulk", status)
const deleteBulk = () => store.dispatch("case_management/deleteBulk")
const showHandoffDialog = () => store.dispatch("case_management/showHandoffDialog")
const showClosedDialog = () => store.dispatch("case_management/showClosedDialog")
</script>
