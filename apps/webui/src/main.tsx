import React from 'react'
import { createRoot } from 'react-dom/client'
const root=document.createElement('div');root.id='root';document.body.appendChild(root)
createRoot(root).render(React.createElement('div',null,'StoryMaker Canvas Demo — v1.6'))
