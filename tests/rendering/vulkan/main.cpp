#define GLFW_INCLUDE_VULKAN
#include <GLFW/glfw3.h>

#include <vulkan/vulkan.h>
#include <iostream>
#include <stdexcept>
#include <stdlib.h>
#include <vector>
#include <optional>
#include <map>
#include <cstring>

const uint32_t WIDTH = 800;
const uint32_t HEIGHT = 800;

const std::vector<const char*> validation_layers = {
    "VK_LAYER_KHRONOS_validation"
};


struct QueueFamilyIndices {
    // Optional structure used to indicate possible nonexistence of queue family
    std::optional<uint32_t> graphicsFamily;

    bool isComplete() {
        return graphicsFamily.has_value();
    }

};


#ifdef NDEBUG
    const bool enable_validation_layers = false;
#else
    const bool enable_validation_layers = true;
#endif


QueueFamilyIndices find_queue_families(VkPhysicalDevice device) {
    QueueFamilyIndices indices;

    uint32_t queue_family_count = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(device, &queue_family_count, nullptr);

    std::vector<VkQueueFamilyProperties> queue_families(queue_family_count);
    vkGetPhysicalDeviceQueueFamilyProperties(device, &queue_family_count, queue_families.data());

    // Need to find at least one queue family that supports VK_QUEUE_GRAPHICS_BIT
    int i = 0;
    for (const auto &queue_family : queue_families) {
        if (queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT) {
            indices.graphicsFamily = i;
        }

        if (indices.isComplete()) {
            break;
        }

        i++;
    }

    return indices;
}


static VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
    VkDebugUtilsMessageSeverityFlagBitsEXT message_severity,
    VkDebugUtilsMessageTypeFlagsEXT message_type,
    const VkDebugUtilsMessengerCallbackDataEXT *pCallbackData,
    void *pUserData
) {
    if (message_severity >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
        std::cerr << "validation layer: " << pCallbackData->pMessage << std::endl;
    }
    return VK_FALSE;
}


void populate_debug_messenger_create_info(VkDebugUtilsMessengerCreateInfoEXT &create_info) {

    create_info = {};
    create_info.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
    create_info.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT | 
        VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
    create_info.messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | 
        VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
    create_info.pfnUserCallback = debugCallback;
    create_info.pUserData = nullptr;
}


VkResult create_debug_utils_messenger_EXT(
    VkInstance instance, 
    const VkDebugUtilsMessengerCreateInfoEXT *pCreateInfo,
    const VkAllocationCallbacks *pAllocator,
    VkDebugUtilsMessengerEXT *pDebugMessenger
) {
    auto func = (PFN_vkCreateDebugUtilsMessengerEXT) vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT");
    if (func != nullptr) {
        return func(instance, pCreateInfo, pAllocator, pDebugMessenger);
    } else {
        return VK_ERROR_EXTENSION_NOT_PRESENT;
    }
}


void setup_debug_messenger(VkInstance instance, VkDebugUtilsMessengerEXT *debug_messenger) {
    if (!enable_validation_layers) return;

    VkDebugUtilsMessengerCreateInfoEXT create_info;
    populate_debug_messenger_create_info(create_info) ;

    if (create_debug_utils_messenger_EXT(instance, &create_info, nullptr, debug_messenger) != VK_SUCCESS) {
        throw std::runtime_error("failed to set up debug messenger!");
    }
}


void destroy_debug_utils_messenger_EXT(
    VkInstance instance, 
    VkDebugUtilsMessengerEXT debugMessenger, 
    const VkAllocationCallbacks *pAllocator
) {
    auto func = (PFN_vkDestroyDebugUtilsMessengerEXT) vkGetInstanceProcAddr(instance, "vkDestroyDebugUtilsMessengerEXT");
    if (func != nullptr) {
        func(instance, debugMessenger, pAllocator);
    }
}


bool check_validation_layer_support() {
    fprintf(stderr, "Checking validation layer support.\n");
    /* Check if requested layers are available */
    uint32_t layer_count;
    vkEnumerateInstanceLayerProperties(&layer_count, nullptr);

    std::vector<VkLayerProperties> available_layers(layer_count);
    vkEnumerateInstanceLayerProperties(&layer_count, available_layers.data());

    for (const char *layer_name : validation_layers) {
        fprintf(stderr, "layer name: %s\n", layer_name);
        bool layer_found = false;

        for (const auto &layer_properties : available_layers) {
            fprintf(stderr, "layer properties name: %s\n", layer_properties.layerName);
            if (strcmp(layer_name, layer_properties.layerName) == 0) {
                layer_found = true;
                break;
            }
        }

        if (!layer_found) {
            return false;
        }
    }

    return true;
}


std::vector<const char*> get_required_extensions() {
    uint32_t glfw_extension_count = 0;
    const char** glfw_extensions;

    std::vector<const char*> extensions(glfw_extensions, glfw_extensions + glfw_extension_count);

    if (enable_validation_layers) {
        extensions.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
    }

    return extensions;
}


bool is_device_suitable(VkPhysicalDevice device) {
    /* Check if device referenced by handle is suitable for use */
    VkPhysicalDeviceProperties deviceProperties;
    vkGetPhysicalDeviceProperties(device, &deviceProperties);

    // Query for support for optional  features like texture compression,
    // 64-bit floats, multi-viewport rendering etc.
    VkPhysicalDeviceFeatures deviceFeatures;
    vkGetPhysicalDeviceFeatures(device, &deviceFeatures);

    return deviceProperties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU && deviceFeatures.geometryShader;
}


int rate_device_suitability(VkPhysicalDevice device) {

    VkPhysicalDeviceProperties device_properties;
    vkGetPhysicalDeviceProperties(device, &device_properties);

    // Query for support for optional  features like texture compression,
    // 64-bit floats, multi-viewport rendering etc.
    VkPhysicalDeviceFeatures device_features;
    vkGetPhysicalDeviceFeatures(device, &device_features);

    int score = 0;

    // Discrete GPUs have a significant performance advantage
    if (device_properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU) {
        score += 1000;
    }

    // Maximum possible size of textures affects graphics quality
    score += device_properties.limits.maxImageDimension2D;

    // Application can't function without geometry shaders
    if (!device_features.geometryShader) {
        return 0;
    }

    // Ensure device has queue families that we desire
    QueueFamilyIndices indices = find_queue_families(device);
    if (!indices.isComplete()) {
        return 0;
    }

    return score;
}


VkPhysicalDevice pick_physical_device(VkInstance instance) {
    // Pick GPU card for our rendering needs
    VkPhysicalDevice physical_device = VK_NULL_HANDLE;

    uint32_t device_count = 0;
    vkEnumeratePhysicalDevices(instance, &device_count, nullptr);

    // If we cannot detect any devices, throw error
    if (device_count == 0) {
        throw std::runtime_error("failed to find GPUs with Vulkan support!");
    }

    // Allocate an array to hold device handles
    std::vector<VkPhysicalDevice> devices(device_count);
    vkEnumeratePhysicalDevices(instance, &device_count, devices.data());

    // Use ordered map to automatically sort candidates by increasing score
    std::multimap<int, VkPhysicalDevice> candidates;

    // Check if physical devices are suitable
    for (const auto& device: devices) {
        int score = rate_device_suitability(device);
        candidates.insert(std::make_pair(score, device));
    }

    // Check if the best candidate is suitable at all
    if (candidates.rbegin()->first > 0) {
        physical_device = candidates.rbegin()->second;
    } else {
        throw std::runtime_error("failed to find a suitable GPU!");
    }

    if (physical_device == VK_NULL_HANDLE) {
        throw std::runtime_error("failed to find a suitable GPU!");
    }

    return physical_device;
}


void create_logical_device() {
    QueueFamilyIndices indices = find_queue_families(physicalDevice);

    // Specify queues to be created
    VkDeviceQueueCreateInfo queueCreateInfo{};
    queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queueCreateInfo.queueFamilyIndex = indices.graphicsFamily.value();
    queueCreateInfo.queueCount = 1;

    // Assign a queue priority
    float queuePriority = 1.0f;
    queueCreateInfo.pQueuePriorities = &queuePriority;

    // Specify device features that we will be using
    VkPhysicalDeviceFeatures deviceFeatures{};

    // Create logical device
    VkDeviceCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    createInfo.pQueueCreateInfos = &queueCreateInfo;
    createInfo.queueCreateInfoCount = 1;
    createInfo.pEnabledFeatures = &deviceFeatures;
    createInfo.enabledExtensionCount = 0;

    if (enable_validation_layers) {
        createInfo.enabledLayerCount = static_cast<uint32_t>(validationLayers.size());
        createInfo.ppEnabledLayerNames = validationLayers.data();
    } else {
        createInfo.enabledLayerCount = 0;
    }

    // Instantiate logical device
    if (vkCreateDevice(physicalDevice, &createInfo, nullptr, &device) != VK_SUCCESS) {
        throw std::runtime_error("failed to create logical device!");
    }
}


void create_instance(VkInstance *instance) {
    if (enable_validation_layers && !check_validation_layer_support()) {
        throw std::runtime_error("Validation layers requested, but not available!");
    }

    VkApplicationInfo app_info{};
    app_info.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    app_info.pApplicationName = "Dino Test";
    app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.pEngineName = "No Engine";
    app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.apiVersion = VK_API_VERSION_1_0;

    // Tell Vulkan driver which global extensions and validation layer
    // we want to use
    VkInstanceCreateInfo create_info{};
    create_info.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    create_info.pApplicationInfo = &app_info;

    auto extensions = get_required_extensions();
    create_info.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
    create_info.ppEnabledExtensionNames = extensions.data();

    // Determine global validation layers to enable
    VkDebugUtilsMessengerCreateInfoEXT debug_create_info{};
    if (enable_validation_layers) {
        create_info.enabledLayerCount = static_cast<uint32_t>(validation_layers.size());
        create_info.ppEnabledLayerNames = validation_layers.data();

        populate_debug_messenger_create_info(debug_create_info);
        create_info.pNext = (VkDebugUtilsMessengerCreateInfoEXT*) &debug_create_info;
    } else {
        create_info.enabledLayerCount = 0;

        create_info.pNext = nullptr;
    }

    // Create Vulkan instance
    if (vkCreateInstance(&create_info, nullptr, instance) != VK_SUCCESS) {
        throw std::runtime_error("failed to create instance!");
    }
}



int main(int argv, char **argc) {

    VkInstance instance;
    VkDebugUtilsMessengerEXT debug_messenger;

    // Initialize GLFW to create window
    glfwInit();
    glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
    glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);

    GLFWwindow *window = glfwCreateWindow(WIDTH, HEIGHT, "Vulkan", nullptr, nullptr);

    // Create Vulkan instance
    try {
        create_instance(&instance);
        setup_debug_messenger(instance, &debug_messenger);
    } catch (const std::exception &e) {
        std::cerr << e.what() <<std::endl;
        return EXIT_FAILURE;
    }

    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
    }

    // Clean up GLFW window
    glfwDestroyWindow(window);
    glfwTerminate();

    // Clean up vk instance
    if (enable_validation_layers) {
        destroy_debug_utils_messenger_EXT(instance, debug_messenger, nullptr);
    }

    vkDestroyInstance(instance, nullptr);
    glfwDestroyWindow(window);
    glfwTerminate();

    return EXIT_SUCCESS;

}