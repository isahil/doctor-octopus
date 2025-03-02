import { useContext } from 'react'
import { LabOptionsContext, OptionsUpdateContext } from '../context'

/**
 * custom hooks for handling the lab options context/state
 * @returns {Object} context for lab options - selected options
 */
export const useLabOptions = () => {
    return useContext(LabOptionsContext)
  }
  
  /**
   * custom hooks for handling the option click context/state
   * @returns {Object} context for handle_option_click - function to handle the dd option click
   */
  export const useOptionsUpdate = () => {
    return useContext(OptionsUpdateContext)
  }