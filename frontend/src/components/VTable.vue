<template>
  <table class="v-table text-bold-24">
    <thead>
      <tr>
        <th
          v-for="header in headers"
          :key="header.key"
        >
          {{ header.label }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="item in items"
        :key="item[primaryKey]"
      >
        <td
          v-for="header in headers"
          :key="header.key"
          v-html="formatValue(item, header)"
        />
      </tr>
    </tbody>
  </table>
</template>

<script setup>
const props = defineProps({
  headers: {
    type: Array,
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
  primaryKey: {
    type: String,
    default: 'id',
  },
  formatters: {
    type: Object,
    default: () => ({}),
  },
})

const formatValue = (item, header) => {
  const value = item[header.key]
  if (props.formatters[header.key]) {
    return props.formatters[header.key](value)
  }
  return value
}
</script>

<style scoped>
.v-table {
  width: 100%;
  border-collapse: collapse;
  font: inherit; /* Inherit font from parent */
  overflow: hidden; /* Ensure rounded corners work properly */
}

.v-table th,
.v-table td {
  padding: 12px 16px; /* Adjusted padding */
  text-align: left;
}
.v-table th {
  background-color: rgba(0, 0, 0, 0.2);
}

.v-table tr {
  height: 65px;
}

.v-table tbody tr:nth-child(even) {
  background-color: rgba(0, 0, 0, 0.075); /* Add alternating row colors */
}
</style>
