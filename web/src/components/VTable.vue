<template>
  <table class="v-table">
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
  border-radius: 8px;
  overflow: hidden; /* Ensure rounded corners work properly */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Add subtle shadow */
}

.v-table th,
.v-table td {
  padding: 12px 16px; /* Adjusted padding */
  text-align: left;
  border-bottom: 1px solid #ddd; /* Add subtle bottom border */
}

.v-table thead {
  background: linear-gradient(to bottom, #f8f8f8, #f0f0f0); /* Light gradient for header */
}

.v-table thead th {
  font-weight: 600; /* Bold header text */
  color: #333333; /* Dark text color */
}

.v-table tbody tr:nth-child(even) {
  background-color: #f9f9f9; /* Add alternating row colors */
}

.v-table tbody td {
  color: #333333;
}
</style>
