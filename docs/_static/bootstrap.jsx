import React, {useState} from 'react';
import ReactDOM from 'react-dom';

import Prism from 'prismjs';
import 'prismjs/components/prism-protobuf'

const LANGUAGES = [
  {value: 'python', title: 'Python'},
  // {value: 'nodejs', title: 'NodeJS'},
  // {value: 'golang', title: 'Go'},
];

const WireType = {
    Input: 1,
    Output: 2,
};

const Accessibility = {
  Local: 'LOCAL',
  Namespace: 'NAMESPACE',
  Cluster: 'CLUSTER',
  External: 'EXTERNAL',
};

const Visibility = {
  Private: "PRIVATE",
  Headless: "HEADLESS",
  Internal: "INTERNAL",
  Public: "PUBLIC",
};

const Wires = [
  {
    runtime: "python",
    type: WireType.Input,
    value: "harness.wires.grpclib.client.ChannelWire",
    configType: "harness.grpc.Channel",
    dependencies: ['grpclib', 'protobuf'],
  },
  {
    runtime: "python",
    type: WireType.Output,
    value: "harness.wires.aiohttp.web.ServerWire",
    configType: "harness.http.Server",
    dependencies: ['aiohttp', 'cchardet'],
  },
];

const Imports = {
  'harness.grpc.Channel': 'harness/grpc.proto',
  'harness.http.Server': 'harness/http.proto',
};

function useSetter(setter) {
  return (event) => {
    setter(event.target.value)
  }
}

function itemSetter(value, setValue, i, name) {
  return (itemValue) => {
    setValue([
      ...value.slice(0, i),
      {...value[i], [name]: itemValue},
      ...value.slice(i + 1),
    ]);
  }
}

function itemDeleter(value, setValue, i) {
  return () => {
    setValue([
      ...value.slice(0, i),
      ...value.slice(i + 1),
    ]);
  }
}

function formatField(i, wire, options) {
  return `${wire.configType} ${wire.configName} = ${i} [\n        ${options.join(',\n        ')}\n    ];`;
}

function formatInput(i, wire, kubeEnabled) {
  let options = [`(harness.wire).input = "${wire.value}"`];
  if (kubeEnabled) {
    options.push(`(harness.wire).access = ${wire.accessibility}`);
  }
  return formatField(i, wire, options);
}

function formatOutput(i, wire, kubeEnabled) {
  let options = [`(harness.wire).output = "${wire.value}"`];
  if (kubeEnabled) {
    options.push(`(harness.wire).visibility = ${wire.visibility}`);
  }
  return formatField(i, wire, options);
}

function renderConfig(serviceName, kubeEnabled, repository, inputs, outputs) {
  const imports = ['harness/wire.proto'];
  inputs.map(w => {
    imports.push(Imports[w.configType]);
  });
  outputs.map(w => {
    imports.push(Imports[w.configType]);
  });

  let sourceLines = [
    `syntax = "proto3";`,
    '',
    `package ${serviceName};`,
  ];
  sourceLines.push('');
  imports.map(value => sourceLines.push(`import "${value}";`));
  sourceLines.push('');
  sourceLines.push(`message Configuration {`);
  sourceLines.push(`    option (harness.service).name = "${serviceName}";`);
  if (kubeEnabled) {
    sourceLines.push(`    option (harness.service).container.repository = "${repository}";`);
  }
  if (inputs.length > 0 || outputs.length > 0) {
    sourceLines.push('');
  }
  let fieldNumber = 1;
  inputs.map(w => {
    sourceLines.push(`    ${formatInput(fieldNumber, w, kubeEnabled)}`);
    fieldNumber++;
  });
  outputs.map(w => {
    sourceLines.push(`    ${formatOutput(fieldNumber, w, kubeEnabled)}`);
    fieldNumber++;
  });
  sourceLines.push('}');

  return Prism.highlight(
    sourceLines.join('\n'),
    Prism.languages.protobuf,
    'protobuf',
  );
}

function Input(props) {
  return (
    <div>
      <label>Name</label>
      <input type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
      <span>{props.wire.value}</span>
      {props.kubeEnabled &&
        <select value={props.wire.accessibility} onChange={useSetter(props.setAccessibility)}>
          {Object.entries(Accessibility).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
      }
      <button onClick={props.delete}>Delete</button>
    </div>
  )
}

function Output(props) {
  return (
    <div>
      <label>Name</label>
      <input type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
      <span>{props.wire.value}</span>
      {props.kubeEnabled &&
        <select value={props.wire.visibility} onChange={useSetter(props.setVisibility)}>
          {Object.entries(Visibility).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
      }
      <button onClick={props.delete}>Delete</button>
    </div>
  )
}

function AddWireDialog(props) {
  const [wire, setWire] = useState("");

  function addWire(event) {
    props.addWire(wire);
  }

  return <div>
    <label>
      New Wire
      <select value={wire} onChange={useSetter(setWire)}>
        <option key={-1} value={""}>--- select ---</option>
        {Wires.map((wire, i) => {
          return <option key={i} value={wire.value}>{wire.value}</option>
        })}
      </select>
    </label>
    <button onClick={addWire} disabled={wire === ""}>Add</button>
  </div>
}

function collectDependencies(inputs, outputs) {
  const items = new Set(['harness']);
  inputs.map(w => {
    w.dependencies.map(v => items.add(v));
  });
  outputs.map(w => {
    w.dependencies.map(v => items.add(v));
  });
  return Array.from(items).sort();
}

function Bootstrap() {
  const [serviceName, setServiceName] = useState('whisper');
  const [runtime, setRuntime] = useState('python');

  const [kubeEnabled, setKubeEnabled] = useState(false);
  const [repository, setRepository] = useState('');

  const [inputs, setInputs] = useState([]);
  const [outputs, setOutputs] = useState([]);

  function addWire(name) {
    let wire = Wires.find(wire => wire.value === name);
    if (wire.type === WireType.Input) {
      setInputs([...inputs, {
        ...wire,
        configName: '',
        accessibility: Accessibility.Cluster,
      }]);
    } else if (wire.type === WireType.Output) {
      setOutputs([...outputs, {
        ...wire,
        configName: '',
        visibility: Visibility.Internal,
      }]);
    } else {
      throw `Unknown wire type: ${wire.type}`
    }
  }

  let configMarkup = {__html: renderConfig(
    serviceName, kubeEnabled, repository, inputs, outputs,
  )};

  const dependencies = collectDependencies(inputs, outputs);

  return (
    <div className="bootstrap">
      <div>
        <label>
          Service Name
          <input type="text" value={serviceName} onChange={useSetter(setServiceName)}/>
        </label>
      </div>
      <div>
        <span>Runtime:</span>
        {LANGUAGES.map(({value, title}) => {
          return (
            <span key={value}>
              <label>
                <input type="radio" value={value}
                       checked={value === runtime}
                       onChange={useSetter(setRuntime)}/>
                {title}
              </label>
            </span>
          )
        })}
      </div>
      <div>
        <label>
          <input type="checkbox" checked={kubeEnabled} onChange={e => {setKubeEnabled(!kubeEnabled)}}/>
          With Kubernetes
        </label>
      </div>
      {kubeEnabled && <div>
        <label>
          Docker Image Repository
          <input type="text" value={repository} onChange={useSetter(setRepository)}/>
        </label>
      </div>}
      <div>
        <AddWireDialog addWire={addWire} />
      </div>
      <div>
        {inputs.map((w, i) => {
          return <Input key={i}
                        wire={w}
                        kubeEnabled={kubeEnabled}
                        setConfigName={itemSetter(inputs, setInputs, i, 'configName')}
                        setAccessibility={itemSetter(inputs, setInputs, i, 'accessibility')}
                        delete={itemDeleter(inputs, setInputs, i)}
          />
        })}
      </div>
      <div>
        {outputs.map((w, i) => {
          return <Output key={i}
                         wire={w}
                         kubeEnabled={kubeEnabled}
                         setConfigName={itemSetter(outputs, setOutputs, i, 'configName')}
                         setVisibility={itemSetter(outputs, setOutputs, i, 'visibility')}
                         delete={itemDeleter(outputs, setOutputs, i)}
          />
        })}
      </div>
      <div>
        <span>Configuration:</span>
        <div>
          <pre dangerouslySetInnerHTML={configMarkup}/>
        </div>
      </div>
      <div>
        <span>Dependencies:</span>
        <pre>{dependencies.join('\n')}</pre>
      </div>
    </div>
  )
}

const mountPoint = document.getElementById('placeholder');
ReactDOM.render(<Bootstrap/>, mountPoint);
