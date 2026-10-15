delete __dirname;
delete __filename;
// delete global
// delete process

function watch(obj, name, visited = new WeakSet()) {
    // 防止循环引用导致无限递归
    if (obj === null || typeof obj !== 'object' || visited.has(obj)) {
        return obj;
    }

    visited.add(obj);

    // 检查原型链访问
    const checkPrototypeChain = (target, property) => {
        let current = target;
        while (current) {
            if (Object.prototype.hasOwnProperty.call(current, property)) {
                return false; // 属性直接存在于当前对象上
            }
            current = Object.getPrototypeOf(current);
            if (current && current !== Object.prototype && current !== null) {
                console.log(`原型链检测:true (对象: ${name}, 属性: ${property})`);
                return true;
            }
        }
        return false;
    };

    return new Proxy(obj, {
        get: function (target, property, receiver) {
            try {
                // 排除一些不常见的或可能导致问题的属性
                if (typeof property === 'symbol' || property === 'constructor' || property === '__proto__') {
                    return Reflect.get(target, property, receiver);
                }

                if (property === 'crypto' || property === 'navigator' || property === 'window') {
                    return target[property];
                }
                const value = Reflect.get(target, property, receiver);
                // if (!value) {
                    // 深度监听嵌套对象
                    if (typeof value === 'object' && value !== null) {
                        // 为嵌套对象生成一个更具体的名称
                        const nestedName = `${name}.${String(property)}`;
                        return watch(value, nestedName, visited);
                    }

                    // 打印属性访问信息
                    console.log(`对象 => ${name}, 读取属性: ${String(property)}, 值为: ${typeof value === 'function' ? 'function' : value}, 类型为: ${typeof value}`);

                    // 检测原型链访问
                    // 如果属性不在 target 上，但通过原型链访问到，则标记为 true
                    if (!Object.prototype.hasOwnProperty.call(target, property)) {
                        checkPrototypeChain(target, property);
                    }

                    // 检测描述符
                    const descriptor = Object.getOwnPropertyDescriptor(target, property);
                    if (descriptor) {
                        if (descriptor.get || descriptor.set) {
                            console.log(`特殊检测: 存在Getter/Setter (对象: ${name}, 属性: ${String(property)})`);
                        }
                        if (!descriptor.writable && !descriptor.get) {
                            console.log(`特殊检测: 只读属性 (对象: ${name}, 属性: ${String(property)})`);
                        }
                        if (!descriptor.configurable) {
                            console.log(`特殊检测: 不可配置属性 (对象: ${name}, 属性: ${String(property)})`);
                        }
                    // }
                }
            } catch (e) {
                console.error(`Error in get trap for ${name}.${String(property)}:`, e);
            }
            return Reflect.get(target, property, receiver);
        },
        set: (target, property, newValue, receiver) => {
            try {
                console.log(`对象 => ${name}, 设置属性: ${String(property)}, 值为: ${typeof newValue === 'function' ? 'function' : newValue}, 类型为: ${typeof newValue}`);
            } catch (e) {
                console.error(`Error in set trap for ${name}.${String(property)}:`, e);
            }
            return Reflect.set(target, property, newValue, receiver);
        },
        // 捕获 in 操作符
        has: function (target, property) {
            console.log(`对象 => ${name}, in 操作符检测属性: ${String(property)}`);
            return Reflect.has(target, property);
        },
        // 捕获 delete 操作符
        deleteProperty: function (target, property) {
            console.log(`对象 => ${name}, 删除属性: ${String(property)}`);
            return Reflect.deleteProperty(target, property);
        },
        // 捕获 Object.keys(), Object.values(), Object.entries() 等操作
        ownKeys: function (target) {
            console.log(`对象 => ${name}, 获取自身所有键`);
            return Reflect.ownKeys(target);
        },
        // 捕获 Object.defineProperty()
        defineProperty: function (target, property, descriptor) {
            console.log(`对象 => ${name}, 定义属性: ${String(property)}`);
            return Reflect.defineProperty(target, property, descriptor);
        },
        // 捕获 Object.setPrototypeOf()
        setPrototypeOf: function (target, prototype) {
            console.log(`特殊检测: setPrototypeOf 被调用 (对象: ${name})`);
            return Reflect.setPrototypeOf(target, prototype);
        },
        // 捕获 Object.getPrototypeOf()
        getPrototypeOf: function (target) {
            console.log(`特殊检测: getPrototypeOf 被调用 (对象: ${name})`);
            return Reflect.getPrototypeOf(target);
        },
        getOwnPropertyDescriptor: function (target, property) {
            console.log(`特殊检测: getOwnPropertyDescriptor 被调用 (对象: ${name}, 属性: ${String(property)})`);
            return Reflect.getOwnPropertyDescriptor(target, property);
        },
        toString: function (target) {
            console.log(`特殊检测: toString 被调用 (对象: ${name})`);
            return Reflect.toString(target);
        }
    });
}

window = globalThis
window.top = window
window.ActiveXObject = undefined
window.XMLHttpRequest = function (args) {
    console.log('window.XMLHttpRequest("' + args + '")')
}
window.addEventListener = function (args) {
    console.log('window.addEventListener("' + args + '")')
}
window.attachEvent = function (args) {
    console.log('window.attachEvent("' + args + '")')
}

Document = function () {
}
div = {
    getElementsByTagName: function (tagName) {
        console.log('document.createElement("div").getElementsByTagName("' + tagName + '")');
        if (tagName === 'i') {
            return []
        }
        else {
            return []
        }

    },
    innerHTML: function (args) {
        console.log('div 的 innerHTML 接收的参数', args)
    },
}
div = watch(div, 'div标签')
a = {}
a = watch(a, 'a标签')
form = {}
form = watch(form, 'form标签')
input = {}
input = watch(input, 'input标签')
Object.defineProperty(Document.prototype, 'createElement', {
    value: function (tagName) {
        console.log('document.createElement("' + tagName + '")');
        if (tagName === 'div') {
            return div
        }
        if (tagName === 'a') {
            return a
        }
        if (tagName === 'form') {
            return form
        }
        if (tagName === 'input') {
            return input
        }else {
            return []
        }
    }
})
Object.defineProperty(Document.prototype, 'appendChild', {
    value: function (tagName) {
        console.log('document.appendChild("' + tagName + '")');
    }
})
Object.defineProperty(Document.prototype, 'removeChild', {
    value: function (tagName) {
        console.log('document.removeChild("' + tagName + '")');
    }
})
script1 = {
    // src: '',
    getAttribute: function (args) {
        console.log('script1 的 getAttribute接受的参数:', args)
        if (args === 'r') {
            return 'm'
        }else {
            return []
        }
    },
    parentElement: {
        removeChild: function (args) {
            console.log('script1 的 removeChild接受的参数:', args)
        }
    },
    innerText: function (args) {
        console.log('script1 的 innerText 接收的参数', args)

    }
}
script2 = {
    getAttribute: function (args) {
        console.log('script2 的 getAttribute接受的参数:', args)
        if (args === 'r') {
            return 'm'
        }else {
            return []
        }
    },
    parentElement: {
        removeChild: function (args) {
            console.log('script2 的 removeChild接受的参数:', args)
        }
    }
}

meta = {
    id: "FbkwzLN5XOx0",
    content: "content123",
    // content: "FM96SU.AAQzga_4q29ZjvRZc4inuboIkG9c.yYvhq3IDgtTMDaotwCvyAfkUfeiakSjvrzMtHztiC62qUEEUanPVSjgdD7a.FVa3lCnyfaM6ZywuzeqQP32xRdjL1HO2gus28KMwiKdHyW2d07E4umtQZx_vZWNnGyyJ_M6J28dy5YkO3tzkQsK1_HxtB_ZPgFX4_ieyqUl",
    getAttribute: function (args) {
        console.log('meta2的getAttribute获取的参数:', args)
        if (args === 'r') {
            return 'm'
        }else {
            return []
        }
    },
    parentNode: {
        removeChild: function (args) {
            console.log('meta2的removeChild接受的参数:', args)
        }
    }
}
script1 = watch(script1, 'script1标签')
script2 = watch(script2, 'script2标签')
meta = watch(meta, 'meta标签')
Document.prototype.getElementsByTagName = function (tagName) {
    console.log('document.getElementsByTagName("' + tagName + '")');
    if (tagName === 'script') {
        return [script1, script2]
    }
    if (tagName === 'base') {
        return []
    }
    else {
        return []
    }
}
Document.prototype.getElementById = function (tagName) {
    console.log('document.getElementById("' + tagName + '")');
    if (tagName === 'FbkwzLN5XOx0') {
        return meta
    }
    else if (tagName === 'a'){
            return null
        }else {
            return []
        }
}
Document.prototype.addEventListener = function (tagName) {
    console.log('document.addEventListener("' + tagName + '")');
}
Document.prototype.attachEvent = function (tagName) {
    console.log('document.attachEvent("' + tagName + '")');
}
HTMLDocument = function () {
}
Object.setPrototypeOf(HTMLDocument.prototype, Document.prototype)
document = new HTMLDocument()

Location = function () {
}
Location.prototype = {
    "ancestorOrigins": {},
    "href": "https://qikan.cqvip.com/Qikan/Journal/JournalGuid?from=index",
    "origin": "https://qikan.cqvip.com",
    "protocol": "https:",
    "host": "qikan.cqvip.com",
    "hostname": "qikan.cqvip.com",
    "port": "",
    "pathname": "/Qikan/Journal/JournalGuid",
    "search": "?from=index",
    "hash": ""
}
Location = watch(Location, 'Location')
location = new Location()

Navigator = function () {
}
Navigator.prototype = {
    appCodeName: "Mozilla",
    appName: "Netscape",
    appVersion: "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    product: "Gecko",
    productSub: "20030107",
    language: "zh-CN",
    languages: [
        "zh-CN",
        "zh"
    ],
    hardwareConcurrency: 16,
    platform: "Win32",
    webdriver: false,
}
Navigator = watch(Navigator, 'Navigator')
navigator = new Navigator();
window = watch(window, 'window');
document = watch(document, 'document');
location = watch(location, 'location');
navigator = watch(navigator, 'navigator');
setTimeout = function () {
}
setInterval = function () {
}

// require('./qk_envs')
!"sz_fun"

"@func"

function RS_6() {
    const tm = document.cookie.toString().split(';')[0].split('=')

    return tm
}

console.log(RS_6());
// console.log(RS_6()['value'].length);