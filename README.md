# 1. 基于深度学习模型的C程序自动生成



## 1.1. 概述

在本文中，我们介绍了一个用于生成 C 语言代码的工具。我们的工具从 GitHub 中收集的数十万行 C 语言代码中学习代码的语义和结构，并通过基于深度学习模型的机器学习模型来自动生成 C 语言程序。此外，我们使用一个驱动脚本来执行生成的 C 语言代码，以测试生成代码的性能。

图1展示了我们系统的框架。我们的方法基于 LLama 模型以及 GitHub 中真实的 C 语言程序，通过机器学习的方法进行 C 语言代码的生成。我们的目标是，基于我们生成的高质量 C 语言数据集，能够在下游任务上训练出更好、更准确的分类模型。我们希望，通过我们生成的高质量 C 语言代码，可以显著提高下游任务的效果。



## 1.2. 系统设计

如 Figure 1 所示，我们的代码生成框架共分为三个部分：数据收集模块，预处理模块，以及代码生成模块。

首先，我们使用数据收集模块，用于自动从 GitHub 爬取代码数据，以解决我们生成框架中数据的获取问题。

其次，预处理模块在代码生成中极为重要，包括代码标准化和向量化两个部分。代码向量化主要是将不同关键字转化为令牌，其余非关键字每个字符作为一个令牌，将不同令牌表示为向量。然后，我们的模型需要对预处理后的数据进行编码训练，对模型参数进行再训练的优化调整。

最后，如 Figure 1 所示，我们的数据生成模块接受一个 prompt 指令，实现 C 语言程序的生成。

![img](.\fig\1.png) 

​																										**Figure** **1 代码生成框架**

 

### 1.2.1数据收集模块

深度学习需要大量的数据来支持模型的训练。在本项工作中，我们需要对编程语言进行建模，这意味着我们需要大量真实的源代码。为了收集这些数据，我们利用了开源数据库 GitHub 上的公共存储库。这本身就是一项具有挑战性的任务，因为程序员在编写代码时具有完全不同的代码风格，这意味着要收集一种尽可能标准的 C 语言训练集是不容易的。因此，我们选择了循环代码作为我们的探索起点。最终，我们收集了包括 LLVM-testsuite 循环 benchmark 在内的超过 80 万行代码。我们使用构建在 LLVM 上的脚本，对从 GitHub 中提取的原始 C 语言循环数据集进行了过滤和重写。



### 1.2.2预处理模块

基于 LLVM 的预处理模块由两部分组成：

1. **编译过滤器**：接受一个 C 语言文件作为输入，并返回它是否包含可编译的、可执行的 C 语言代码。在这里，我们丢弃了任何不能编译的代码块。

2. **代码重写器**：编程语言和自然语言存在许多语法上的差异。例如，代码中的注释内容以及变量名的选择问题。我们认为这些歧义是由于人为编程风格导致的，因此，我们开发了一个工具来标准化这些人为引入的代码差异，使代码更容易让机器学习。这个标准化过程分为三步：

   - 删除注释和声明
   - 标准化常量名、函数名、变量名
   - 强制标准化代码风格

   图2展示了代码重写过程的一个示例。这个过程的另一个好处是代码大小的减少，主要是由于删除了注释和多余的空白字符。最终的语料库包含 13 万行 C 语言循环代码。变量和令牌重写可使向量化模型的词汇表大小减少约 84%。

![img](.\fig\2.jpg) 

**Figure** **2(a)** **重写前的C语言代码**

![img](.\fig\3.jpg) 

**Figure** **2(b)** **重写后的C语言代码**



### 1.2.3 数据生成模块

##### **一、模型结构**

我们的工具利用无监督机器学习技术来生成有效的、可执行的程序代码。我们使用了最先进的深度学习建模技术 Llama 来实现这项任务。基于 Transformer 的深度学习体系结构框架，我们在 C 语言的语料库上学习一个代码生成模型。Llama 模型由多层单向 Transformer 的解码器部分构成，本质上是自回归模型，即每次产生新单词后，将新单词加到原输入句后面，作为新的输入句。

如图3所示，这个模型是一个改进的 Transformer 架构，采用了前置的 RMSNorm 稳定训练，利用 RoPE 旋转式位置编码来维持序列位置信息，并使用因果掩码确保信息流的单向性。它通过 LLaMA 机制扩展上下文窗口，允许模型访问更广泛的历史信息，同时使用分组查询注意力机制提高效率，其 MLP 部分含有特殊的门控线性层设计，适用于处理大规模代码数据，特别是在需要捕捉长距离依赖关系时。

![img](.\fig\4.jpg)

​																														**Figure** **3模型结构**

##### **二、**代码生成过程

为了调优一个训练好的 Llama 模型，我们只需要简单地提供一个预先定义好的 Prompt。具体来说，每一个解码器模块处理单词的步骤如下：

1. 编码：模型接收一个预先定义的 Prompt，通常这是一段代码的开头或一段注释，用于说明要生成的代码的功能。输入的 Prompt 会被分解成一个个的 token，这些 token 可能是关键字、变量名、操作符等。每个 token 都会被转换成高维空间中的向量，这个向量可以捕捉其语义和语法信息。为了帮助模型理解各个 token 之间的位置关系，我们会为这些嵌入加入位置编码。
2. 解码：在解码器模块中，每个 token 的嵌入将通过自注意力机制与之前的 token 结合，以生成下一个 token 的输出。模型会使用一个固定大小的窗口来限制在生成每个新 token 时所能参考的上下文范围。模型会在每一步生成具有最高概率的 token，这个过程可能会受到前文提到的因果掩码的影响，以确保生成的代码保持逻辑上的正确顺序。此外，模型需要能够检测何时完成整段代码的生成，这通常是通过生成特定的结束 token 来实现的。

整个过程中，模型将持续接收输入的 token，生成新的 token，并调整其内部权重以优化生成的代码质量。这个过程会一直持续，直到模型生成了完整的代码段落。在实际训练时，我们使用随机梯度下降来 fine-tune 这个预训练的 Llama 模型，初始学习率为 0.002，在一台使用 NVIDIA GTX 3080 的单一机器上进行训练用了 40 小时的时间。需要说明的是，训练网络是一次性的成本，训练过的网络可以部署到低配置的计算机上使用。



##### **三、**数据集说明

- "instruction"：任务的指导说明，即生成 C 语言源代码。
- "input"：输入的格式或内容，即输入是生成 C 源代码的指令。
- "output"：期望的输出，即生成的 C 源代码。

```
"instruction": "C source code",
"input": "Generate C source code",
"output": "#include <math.h> ..."
```



## 2. 代码说明及实验

![img](.\fig\5.jpg)	 

**Figure** **4 代码生成实验示意**



## 2.1. 安装

这段代码是用于下载代码和预训练模型，并设置项目环境的步骤。

```
# 下载代码以及预训练模型
git lfs clone https://huggingface.co/datasets/dsslll/CodeGen.git

# 进入项目文件
cd src

# 创建虚拟环境，基于 Python 3.10 版本
conda create -n codegen python==3.10 -y

# 激活虚拟环境
conda activate codegen

# 安装依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -e .
```

#### 2.1.1 代码分布说明

```
01huawei/
├─ C程序生成文档.md                
├─ fig/                         
├─ pretrained_model/            # 预训练模型文件夹
├─ compile_test/                # 编译运行测试文件夹
|  ├─ select_run.py					# 测试生成的C语言代码文件
├─ finetune/                    # 微调相关文件夹
│  ├─ alpaca-lora-7b/           	# 参数文件夹
│  ├─ CodeLlama-7b-hf/          	# 底层预训练模型
│  ├─ HW-cost-model-dataset/    # 数据集文件夹
│  │  ├─ cBench/                	# cBench 数据集文件夹
│  │  └─ dataset/               	# C数据集文件夹
│  ├─ lora-alpaca/              # 模型参数
│  ├─ templates/                
│  └─ utils/                    # 实用工具文件夹
│  │  ├─ finetune.py
│  │  ├─ generate.py
├─ src/                         # 程序代码文件夹
│  ├─ Cgen.py                   # 主程序代码文件
│  ├─ llama/                    # 调用函数代码文件夹
│  │  ├─ generation.py          	# 生成函数代码文件
│  │  ├─ model.py               	# 模型函数代码文件
│  │  ├─ tokenizer.py           	
│  │  └─ __init__.py            	
├─ output.txt                   # 生成的C语言代码保存的文件
└─ requirements.txt             # 安装文档
```

## 2.2. 代码使用说明

#### 2.2.1 代码生成：

在这一部分，我们使用我们训练好的模型进行C语言代码的生成，具体使用命令如下：

```
# 参数说明：
# --saveto [yourfolder]: 指定生成的代码样本将被保存的输出目录或文件。
#                        将 [yourfolder] 替换为所需的文件路径或名称。例如, 'output.txt'。
#                        如果指定了目录，请确保其存在；否则，脚本可能无法写入输出。
#
# --iteration [the number of code samples]: 表示脚本应生成多少个代码样本。
#                                           用整数值替换 [the number of code samples]，例如，1000。
#                                           此参数控制代码生成循环将运行多少次。

Python Cgen.py --saveto [yourfolder] --iteration [the number of code samples]

# 示例命令：
# Python Cgen.py --saveto 'output.txt' --iteration 1000
# 此示例命令将运行 Cgen.py 脚本，生成1000个代码样本，并将它们保存到 'output.txt'。

```

#### 2.2.2 微调模型

在这一部分，用户也可以在自己的数据集上进行fine-tune，来增强模型的训练效果。在针对我们下游模型进行微调时，我们采用基于Alpaca-LoRA的训练方式对我们的基准模型进行微调。具体命令如下：

```
#示例命令
python finetune/finetune.py \
    --base_model='finetune/CodeLlama-7b-hf' \  # 指定基础模型的名称或路径
    --data_path 'finetune/dataset/Cdataset' \         # 指定数据集的路径
    --num_epochs=10 \                              # 指定微调的迭代次数
    --cutoff_len=512 \                              # 指定文本截断的长度
    --group_by_length \                             # 指定是否根据文本长度分组
    --output_dir 'finetune/lora-alpaca' \                  # 指定微调后模型的输出目录
    --lora_target_modules='[q_proj,k_proj,v_proj,o_proj]' \  # 指定要应用 LORA 的目标模块
    --lora_r=16 \                                   # 指定 LORA 中的参数 r 的值
    --micro_batch_size=8                            # 指定微批次大小
```



## 2.3. 实验说明

训练数据：在实验测试中我们首先从github爬取了约7000个C语言的文件。

训练方式：我们使用了LLama在大型语料库上预训练好的模型，并将C文件自动划分为不同的输入token和输出token供LLama模型迁移训练。

结果：能够生成可运行的C代码。具体实验示意图见图4，我们另附了代码生成的视频文件codegen.mp4，相关代码和使用说明见“fig”文件夹内。

 


